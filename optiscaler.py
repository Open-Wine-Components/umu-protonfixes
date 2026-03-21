"""Download and setup OptiScaler as a prefix-managed payload."""

import configparser
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
PAYLOAD_DIR = 'payload'
BACKUP_DIR = 'backups'
MANIFEST_FILE = 'manifest.json'
INI_FILE = 'OptiScaler.ini'
MAIN_DLL = 'OptiScaler.dll'
ENV_VAR = 'PROTON_OPTISCALER'
PATH_VAR = 'PROTON_OPTISCALER_PATH'
CONFIG_VAR = 'PROTON_OPTISCALER_CONFIG'
TRUE_VALUES = {'1'}
SUPPORTED_PROXIES = (
    'auto',
    'winmm',
    'dxgi',
    'version',
    'dbghelp',
    'winhttp',
    'wininet',
    'd3d12',
)
AUTO_PROXIES = ('winmm', 'dxgi', 'version', 'dbghelp', 'winhttp', 'wininet', 'd3d12')
DEFAULT_VERSION = '0.7.9'
DEFAULT_ASSET_NAME = f'OptiScaler_{DEFAULT_VERSION}.7z'
DEFAULT_URL = (
    'https://github.com/optiscaler/OptiScaler/releases/download/'
    f'v{DEFAULT_VERSION}/{DEFAULT_ASSET_NAME}'
)


def _managed_dir(compat_dir: str) -> Path:
    return Path(compat_dir) / MANAGED_DIR


def _system32_dir(prefix_dir: str) -> Path:
    return Path(prefix_dir) / 'drive_c/windows/system32'


def _load_manifest(compat_dir: str) -> dict:
    path = _managed_dir(compat_dir) / MANIFEST_FILE
    if not path.is_file():
        return {}

    try:
        with path.open(encoding='utf-8') as fd:
            data = json.load(fd)
        return data if isinstance(data, dict) else {}
    except Exception as exc:
        log.warn(f'Failed to read OptiScaler manifest "{path}"')
        log.warn(repr(exc))
        return {}


def _save_manifest(compat_dir: str, manifest: dict) -> None:
    path = _managed_dir(compat_dir) / MANIFEST_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as fd:
        json.dump(manifest, fd, indent=2, sort_keys=True)
        fd.write('\n')


def _remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
    elif path.is_dir():
        shutil.rmtree(path)


def _set_env_list(
    env: MutableMapping[str, str], key: str, value: str, separator: str = ';'
) -> None:
    parts = [part for part in env.get(key, '').split(separator) if part]
    if value not in parts:
        parts.append(value)
    if parts:
        env[key] = separator.join(parts)
    elif key in env:
        del env[key]


def _drop_env_list(
    env: MutableMapping[str, str], key: str, value: str, separator: str = ';'
) -> None:
    parts = [part for part in env.get(key, '').split(separator) if part and part != value]
    if parts:
        env[key] = separator.join(parts)
    elif key in env:
        del env[key]


def _resolve_payload_override(env: Mapping[str, str]) -> Optional[Path]:
    payload_path = env.get(PATH_VAR, '').strip()
    if not payload_path:
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
    with dst.open('wb') as dst_fd:
        with urllib.request.urlopen(request, timeout=30) as url_fd:
            shutil.copyfileobj(url_fd, dst_fd)


def _extract_archive(archive_path: Path, dst: Path) -> None:
    binary = shutil.which('7z') or shutil.which('7zz')
    if binary is None:
        raise RuntimeError('OptiScaler extraction requires the 7z or 7zz binary in PATH')

    _remove_path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='optiscaler-payload-') as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        subprocess.run(
            [binary, 'x', str(archive_path), f'-o{temp_dir}'],
            check=True,
            capture_output=True,
            text=True,
        )
        shutil.copytree(_find_payload_root(temp_dir), dst)


def _ensure_payload(compat_dir: str) -> tuple[Path, list[str]]:
    payload_root = _managed_dir(compat_dir) / PAYLOAD_DIR / 'current'
    if payload_root.joinpath(MAIN_DLL).is_file():
        return payload_root, _payload_files(payload_root)

    archive_path = config.path.cache_dir / 'optiscaler/downloads' / DEFAULT_ASSET_NAME
    if not archive_path.is_file() or archive_path.stat().st_size == 0:
        log.info(f'Downloading OptiScaler from "{DEFAULT_URL}"')
        _download_file(DEFAULT_URL, archive_path)

    log.info(f'Extracting OptiScaler "{archive_path.name}"')
    _extract_archive(archive_path, payload_root)
    return payload_root, _payload_files(payload_root)


def _managed_ini_path(compat_dir: str, payload_root: Path) -> Path:
    ini_path = _managed_dir(compat_dir) / INI_FILE
    payload_ini = payload_root / INI_FILE
    if not payload_ini.is_file():
        raise FileNotFoundError(f'OptiScaler payload is missing "{INI_FILE}"')

    ini_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(payload_ini, ini_path)
    return ini_path


def _apply_ini_overrides(ini_path: Path, config_value: str) -> None:
    if not config_value:
        return

    parser = configparser.RawConfigParser()
    parser.optionxform = str
    parser.read(ini_path, encoding='utf-8')

    for entry in filter(None, (item.strip() for item in config_value.split(';'))):
        option_key, separator, value = entry.partition('=')
        section, dot, key = option_key.partition('.')
        if separator != '=' or dot != '.' or not section or not key:
            log.warn(f'Skipping invalid OptiScaler override "{entry}"')
            continue
        if not parser.has_section(section):
            parser.add_section(section)
        parser.set(section, key, value)

    with ini_path.open('w', encoding='utf-8') as fd:
        parser.write(fd, space_around_delimiters=False)


def _resolve_proxy(proxy: str, previous_proxy: str) -> str:
    proxy = proxy.strip().lower()
    if proxy in TRUE_VALUES:
        proxy = 'auto'
    if proxy not in SUPPORTED_PROXIES:
        raise RuntimeError(f'Unsupported OptiScaler proxy "{proxy}"')
    if proxy != 'auto':
        return proxy
    return previous_proxy if previous_proxy in AUTO_PROXIES else AUTO_PROXIES[0]


def _stage_target(
    compat_dir: str,
    target: Path,
    previous_manifest: dict,
    *,
    managed: bool,
) -> None:
    backup = _managed_dir(compat_dir) / BACKUP_DIR / target.name
    if not target.exists() and not target.is_symlink():
        return
    if previous_manifest.get('enabled') and managed:
        _remove_path(target)
    elif not backup.exists() and not backup.is_symlink():
        backup.parent.mkdir(parents=True, exist_ok=True)
        target.rename(backup)
    else:
        _remove_path(target)


def _restore_target(compat_dir: str, target: Path) -> None:
    backup = _managed_dir(compat_dir) / BACKUP_DIR / target.name
    _remove_path(target)
    if backup.exists() or backup.is_symlink():
        target.parent.mkdir(parents=True, exist_ok=True)
        backup.rename(target)


def _stage_proxy(prefix_dir: str, payload_root: Path, proxy: str, previous_manifest: dict) -> None:
    target = _system32_dir(prefix_dir) / f'{proxy}.dll'
    backup = _system32_dir(prefix_dir) / f'{proxy}-original.dll'
    temp = target.with_name(f'.{target.name}.tmp')
    previous_target = target.with_name(f'.{target.name}.previous')

    if backup.exists() and previous_manifest.get('proxy') != proxy:
        raise RuntimeError(
            f'Cannot stage OptiScaler proxy "{proxy}" because "{backup.name}" already exists'
        )

    _remove_path(temp)
    _remove_path(previous_target)
    shutil.copy2(payload_root / MAIN_DLL, temp)

    try:
        if target.exists() or target.is_symlink():
            if previous_manifest.get('enabled') and previous_manifest.get('proxy') == proxy:
                target.rename(previous_target)
                try:
                    temp.rename(target)
                except Exception:
                    previous_target.rename(target)
                    raise
                _remove_path(previous_target)
                return
            if not backup.exists() and not backup.is_symlink():
                target.rename(backup)
                try:
                    temp.rename(target)
                except Exception:
                    backup.rename(target)
                    raise
                return
            _remove_path(target)

        temp.rename(target)
    finally:
        _remove_path(temp)
        _remove_path(previous_target)


def _restore_proxy(prefix_dir: str, proxy: str) -> None:
    target = _system32_dir(prefix_dir) / f'{proxy}.dll'
    backup = _system32_dir(prefix_dir) / f'{proxy}-original.dll'
    _remove_path(target)
    if backup.exists() or backup.is_symlink():
        backup.rename(target)


def disable_optiscaler(
    compat_dir: str,
    prefix_dir: str,
    env: Optional[MutableMapping[str, str]] = None,
) -> bool:
    """Restore the prefix to its stock state by removing OptiScaler staging."""
    manifest = _load_manifest(compat_dir)
    if not manifest.get('enabled'):
        return False

    system32 = _system32_dir(prefix_dir)
    for filename in (*manifest.get('payload_files', ()), INI_FILE):
        _restore_target(compat_dir, system32 / filename)

    proxy = manifest.get('proxy', '')
    if proxy:
        _restore_proxy(prefix_dir, proxy)
        if env is not None:
            _drop_env_list(env, 'WINEDLLOVERRIDES', f'{proxy}=n,b')

    manifest['enabled'] = False
    _save_manifest(compat_dir, manifest)
    log.info('Disabled OptiScaler for this prefix.')
    return True


def enable_optiscaler(
    payload_root: Path,
    compat_dir: str,
    prefix_dir: str,
    env: MutableMapping[str, str],
    *,
    proxy: str = 'auto',
    config_value: str = '',
    payload_files: Optional[list[str]] = None,
    payload_key: str = 'managed',
) -> bool:
    """Stage a managed OptiScaler payload into the given game prefix."""
    previous_manifest = _load_manifest(compat_dir)
    payload_root = Path(payload_root)
    payload_files = payload_files or _payload_files(payload_root)
    resolved_proxy = _resolve_proxy(proxy, previous_manifest.get('proxy', ''))

    same_state = (
        previous_manifest.get('enabled')
        and previous_manifest.get('proxy') == resolved_proxy
        and set(previous_manifest.get('payload_files', ())) == set(payload_files)
        and previous_manifest.get('payload') == payload_key
    )

    if previous_manifest.get('enabled') and not same_state:
        disable_optiscaler(compat_dir, prefix_dir, env)
        previous_manifest = _load_manifest(compat_dir)

    ini_path = _managed_ini_path(compat_dir, payload_root)
    _apply_ini_overrides(ini_path, config_value)

    if same_state:
        _set_env_list(env, 'WINEDLLOVERRIDES', f'{resolved_proxy}=n,b')
        manifest = dict(previous_manifest)
        manifest.update(
            {
                'enabled': True,
                'payload_files': payload_files,
                'payload': payload_key,
                'proxy': resolved_proxy,
            }
        )
        _save_manifest(compat_dir, manifest)
        log.info(f'Enabled OptiScaler with proxy "{resolved_proxy}".')
        return True

    system32 = _system32_dir(prefix_dir)
    system32.mkdir(parents=True, exist_ok=True)
    managed_names = set(previous_manifest.get('payload_files', ())) | {INI_FILE}
    staged_targets = []
    proxy_staged = False

    try:
        for filename in payload_files:
            target = system32 / filename
            _stage_target(compat_dir, target, previous_manifest, managed=filename in managed_names)
            staged_targets.append(target)
            target.symlink_to(Path(os.path.relpath(payload_root / filename, target.parent)))

        ini_target = system32 / INI_FILE
        _stage_target(compat_dir, ini_target, previous_manifest, managed=True)
        staged_targets.append(ini_target)
        ini_target.symlink_to(Path(os.path.relpath(ini_path, ini_target.parent)))

        _stage_proxy(prefix_dir, payload_root, resolved_proxy, previous_manifest)
        proxy_staged = True
        _set_env_list(env, 'WINEDLLOVERRIDES', f'{resolved_proxy}=n,b')

        manifest = dict(previous_manifest)
        manifest.update(
            {
                'enabled': True,
                'payload_files': payload_files,
                'payload': payload_key,
                'proxy': resolved_proxy,
            }
        )
        _save_manifest(compat_dir, manifest)
    except Exception:
        for target in reversed(staged_targets):
            _restore_target(compat_dir, target)
        if proxy_staged:
            _restore_proxy(prefix_dir, resolved_proxy)
        _drop_env_list(env, 'WINEDLLOVERRIDES', f'{resolved_proxy}=n,b')
        raise

    log.info(f'Enabled OptiScaler with proxy "{resolved_proxy}".')
    return True


def setup_optiscaler(
    env: MutableMapping[str, str], compat_dir: str, prefix_dir: str
) -> None:
    """Setup OptiScaler from Proton-style environment variables.

    usage: setup_optiscaler(g_session.env, g_compatdata.base_dir, g_compatdata.prefix_dir)
    """
    enabled = env.get(ENV_VAR, '').strip()
    if not enabled:
        disable_optiscaler(compat_dir, prefix_dir, env)
        return

    try:
        payload_override = _resolve_payload_override(env)
        if payload_override is not None:
            payload_root = payload_override
            payload_files = _payload_files(payload_root)
            payload_key = str(payload_root)
        else:
            payload_root, payload_files = _ensure_payload(compat_dir)
            payload_key = 'managed'
        enable_optiscaler(
            payload_root,
            compat_dir,
            prefix_dir,
            env,
            proxy='auto' if enabled.lower() in TRUE_VALUES else enabled,
            config_value=env.get(CONFIG_VAR, ''),
            payload_files=payload_files,
            payload_key=payload_key,
        )
    except (FileNotFoundError, RuntimeError, HTTPError, URLError, OSError) as exc:
        log.crit('Failed to setup OptiScaler.')
        log.crit(repr(exc))
