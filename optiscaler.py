"""Download and setup OptiScaler as a prefix-managed payload."""

import json
import os
import shutil
import subprocess
import tempfile
import urllib.request
from collections.abc import Mapping, MutableMapping
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError

from .config import config
from .logger import log


MANAGED_DIR = 'optiscaler-managed'
MANIFEST_FILE = 'manifest.json'
INI_FILE = 'OptiScaler.ini'
MAIN_DLL = 'OptiScaler.dll'
ENV_VAR = 'PROTON_OPTISCALER'
PATH_VAR = 'PROTON_OPTISCALER_PATH'
SUPPORTED_PROXIES = {
    'winmm',
    'dxgi',
    'version',
    'dbghelp',
    'winhttp',
    'wininet',
    'd3d12',
}
DEFAULT_ASSET_NAME = 'OptiScaler_0.7.9.7z'
DEFAULT_URL = (
    'https://github.com/optiscaler/OptiScaler/releases/download/'
    f'v0.7.9/{DEFAULT_ASSET_NAME}'
)


def _backup_path(compat_dir: Path, target: Path) -> Path:
    return Path(compat_dir) / MANAGED_DIR / 'backups' / target.name


def _load_manifest(compat_dir: Path) -> dict:
    path = Path(compat_dir) / MANAGED_DIR / MANIFEST_FILE
    if not path.is_file():
        return {}

    try:
        with path.open(encoding='utf-8') as fd:
            return data if isinstance((data := json.load(fd)), dict) else {}
    except Exception as exc:
        log.warn(f'Failed to read OptiScaler manifest "{path}"')
        log.warn(repr(exc))
        return {}


def _save_manifest(compat_dir: Path, manifest: dict) -> None:
    path = Path(compat_dir) / MANAGED_DIR / MANIFEST_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as fd:
        json.dump(manifest, fd, indent=2, sort_keys=True)
        fd.write('\n')


def _remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
    elif path.is_dir():
        shutil.rmtree(path)


def _path_present(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def _append_override(env: MutableMapping[str, str], proxy: str) -> None:
    value = f'{proxy}=n,b'
    parts = [part for part in env.get('WINEDLLOVERRIDES', '').split(';') if part]
    if value not in parts:
        parts.append(value)
    env['WINEDLLOVERRIDES'] = ';'.join(parts)


def _remove_override(env: MutableMapping[str, str], proxy: str) -> None:
    value = f'{proxy}=n,b'
    parts = [part for part in env.get('WINEDLLOVERRIDES', '').split(';') if part and part != value]
    if parts:
        env['WINEDLLOVERRIDES'] = ';'.join(parts)
    elif 'WINEDLLOVERRIDES' in env:
        del env['WINEDLLOVERRIDES']


def _resolve_payload_override(env: Mapping[str, str]) -> Optional[Path]:
    if not (payload_path := env.get(PATH_VAR, '').strip()):
        return None

    payload_root = Path(payload_path).expanduser().resolve()
    if not payload_root.is_dir():
        raise RuntimeError(f'OptiScaler payload override is not a directory: "{payload_root}"')
    if not payload_root.joinpath(MAIN_DLL).is_file():
        raise FileNotFoundError(f'OptiScaler payload override is missing "{MAIN_DLL}"')
    return payload_root


def _find_payload_root(base_dir: Path) -> Path:
    candidates = sorted(
        {path.parent for path in base_dir.rglob(MAIN_DLL) if path.is_file()},
        key=lambda path: (len(path.relative_to(base_dir).parts), str(path)),
    )
    if not candidates:
        raise FileNotFoundError(f'Unable to locate {MAIN_DLL} in "{base_dir}"')
    return candidates[0]


def _payload_files(payload_root: Path) -> list[str]:
    return sorted(
        path.name
        for path in payload_root.glob('*.dll')
        if path.is_file() and path.name != MAIN_DLL
    )


def _download_file(url: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={'User-Agent': 'umu-protonfixes'})
    with urllib.request.urlopen(request, timeout=30) as url_fd, dst.open('wb') as dst_fd:
        shutil.copyfileobj(url_fd, dst_fd)


def _extract_archive(archive_path: Path, dst: Path) -> None:
    if not (binary := shutil.which('7z') or shutil.which('7zz')):
        raise RuntimeError('OptiScaler extraction requires the 7z or 7zz binary in PATH')

    _remove_path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='optiscaler-payload-') as temp_dir:
        subprocess.run(
            [binary, 'x', str(archive_path), f'-o{temp_dir}'],
            check=True,
            capture_output=True,
            text=True,
        )
        shutil.copytree(_find_payload_root(Path(temp_dir)), dst)


def _ensure_payload(compat_dir: Path) -> Path:
    payload_root = Path(compat_dir) / MANAGED_DIR / 'payload' / 'current'
    if payload_root.joinpath(MAIN_DLL).is_file():
        return payload_root

    archive_path = config.path.cache_dir / 'optiscaler/downloads' / DEFAULT_ASSET_NAME
    if not archive_path.is_file() or archive_path.stat().st_size == 0:
        log.info(f'Downloading OptiScaler from "{DEFAULT_URL}"')
        _download_file(DEFAULT_URL, archive_path)

    log.info(f'Extracting OptiScaler "{archive_path.name}"')
    _extract_archive(archive_path, payload_root)
    return payload_root


def _managed_ini_path(compat_dir: Path, payload_root: Path) -> Path:
    ini_path = Path(compat_dir) / MANAGED_DIR / INI_FILE
    if ini_path.is_file():
        return ini_path

    payload_ini = payload_root / INI_FILE
    if not payload_ini.is_file():
        raise FileNotFoundError(f'OptiScaler payload is missing "{INI_FILE}"')

    ini_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(payload_ini, ini_path)
    return ini_path


def _resolve_proxy(proxy: str) -> str:
    if (proxy := proxy.strip().lower()) not in SUPPORTED_PROXIES:
        raise RuntimeError(f'Unsupported OptiScaler proxy "{proxy}"')
    return proxy


def _stage_target(compat_dir: Path, target: Path) -> None:
    backup = _backup_path(compat_dir, target)
    if not _path_present(target):
        return
    if not _path_present(backup):
        backup.parent.mkdir(parents=True, exist_ok=True)
        target.rename(backup)
    else:
        _remove_path(target)


def _restore_target(compat_dir: Path, target: Path) -> None:
    backup = _backup_path(compat_dir, target)
    _remove_path(target)
    if _path_present(backup):
        target.parent.mkdir(parents=True, exist_ok=True)
        backup.rename(target)


def _stage_proxy(system32: Path, payload_root: Path, proxy: str) -> None:
    target = system32 / f'{proxy}.dll'
    backup = system32 / f'{proxy}-original.dll'
    temp = target.with_name(f'.{target.name}.tmp')

    if _path_present(backup):
        raise RuntimeError(
            f'Cannot stage OptiScaler proxy "{proxy}" because "{backup.name}" already exists'
        )

    _remove_path(temp)
    shutil.copy2(payload_root / MAIN_DLL, temp)
    try:
        if _path_present(target):
            target.rename(backup)
        temp.rename(target)
    except Exception:
        _remove_path(temp)
        if backup.exists() and not _path_present(target):
            backup.rename(target)
        raise
    finally:
        _remove_path(temp)


def _restore_proxy(system32: Path, proxy: str) -> None:
    target = system32 / f'{proxy}.dll'
    backup = system32 / f'{proxy}-original.dll'
    _remove_path(target)
    if _path_present(backup):
        backup.rename(target)


def disable_optiscaler(
    compat_dir: str,
    prefix_dir: str,
    env: Optional[MutableMapping[str, str]] = None,
) -> bool:
    """Restore the prefix to its stock state by removing OptiScaler staging."""
    compat_path = Path(compat_dir)
    system32 = Path(prefix_dir) / 'drive_c/windows/system32'
    manifest = _load_manifest(compat_path)
    if not manifest.get('enabled'):
        return False

    for filename in (*manifest.get('payload_files', ()), INI_FILE):
        _restore_target(compat_path, system32 / filename)

    proxy = manifest.get('proxy', '')
    if proxy:
        _restore_proxy(system32, proxy)
        if env is not None:
            _remove_override(env, proxy)

    manifest['enabled'] = False
    _save_manifest(compat_path, manifest)
    log.info('Disabled OptiScaler for this prefix.')
    return True


def enable_optiscaler(
    payload_root: Path,
    compat_dir: str,
    prefix_dir: str,
    env: MutableMapping[str, str],
    *,
    proxy: str,
) -> bool:
    """Stage a managed OptiScaler payload into the given game prefix."""
    compat_path = Path(compat_dir)
    system32 = Path(prefix_dir) / 'drive_c/windows/system32'
    manifest = _load_manifest(compat_path)
    if manifest.get('enabled'):
        disable_optiscaler(compat_dir, prefix_dir, env)

    payload_files = _payload_files(payload_root)
    resolved_proxy = _resolve_proxy(proxy)
    ini_path = _managed_ini_path(compat_path, payload_root)
    system32.mkdir(parents=True, exist_ok=True)

    staged_targets = []
    proxy_staged = False
    staged_files = [(filename, payload_root / filename) for filename in payload_files]
    staged_files.append((INI_FILE, ini_path))
    try:
        for filename, source in staged_files:
            target = system32 / filename
            _stage_target(compat_path, target)
            staged_targets.append(target)
            target.symlink_to(Path(os.path.relpath(source, target.parent)))

        _stage_proxy(system32, payload_root, resolved_proxy)
        proxy_staged = True
        _append_override(env, resolved_proxy)
        _save_manifest(
            compat_path,
            {
                'enabled': True,
                'payload_files': payload_files,
                'proxy': resolved_proxy,
            },
        )
    except Exception:
        for target in reversed(staged_targets):
            _restore_target(compat_path, target)
        if proxy_staged:
            _restore_proxy(system32, resolved_proxy)
        _remove_override(env, resolved_proxy)
        raise

    log.info(f'Enabled OptiScaler with proxy "{resolved_proxy}".')
    return True


def setup_optiscaler(env: MutableMapping[str, str], compat_dir: str, prefix_dir: str) -> None:
    """Setup OptiScaler from Proton-style environment variables.

    usage: setup_optiscaler(g_session.env, g_compatdata.base_dir, g_compatdata.prefix_dir)
    """
    enabled = env.get(ENV_VAR, '').strip()
    if not enabled:
        disable_optiscaler(compat_dir, prefix_dir, env)
        return

    try:
        payload_root = _resolve_payload_override(env) or _ensure_payload(Path(compat_dir))
        enable_optiscaler(
            payload_root,
            compat_dir,
            prefix_dir,
            env,
            proxy=enabled,
        )
    except (FileNotFoundError, RuntimeError, HTTPError, URLError, OSError) as exc:
        log.crit('Failed to setup OptiScaler.')
        log.crit(repr(exc))
