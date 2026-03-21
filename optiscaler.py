"""Download and setup OptiScaler as a prefix-managed payload."""

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError

from .config import config
from .logger import log


__managed_dir = 'optiscaler-managed'
__payload_dir = 'payload'
__backup_dir = 'backups'
__manifest_file = 'manifest.json'
__ini_file = 'OptiScaler.ini'
__main_dll = 'OptiScaler.dll'
__env_var = 'PROTON_OPTISCALER'
__path_var = 'PROTON_OPTISCALER_PATH'
__config_var = 'PROTON_OPTISCALER_CONFIG'
__true_values = {'1'}
__supported_proxies = (
    'auto',
    'winmm',
    'dxgi',
    'version',
    'dbghelp',
    'winhttp',
    'wininet',
    'd3d12',
)
__auto_proxies = ('winmm', 'dxgi', 'version', 'dbghelp', 'winhttp', 'wininet', 'd3d12')
__default_version = '0.7.9'
__default_asset_name = f'OptiScaler_{__default_version}.7z'
__default_url = (
    'https://github.com/optiscaler/OptiScaler/releases/download/'
    f'v{__default_version}/{__default_asset_name}'
)


def _managed_dir(compat_dir: str) -> Path:
    return Path(compat_dir) / __managed_dir


def _system32_dir(prefix_dir: str) -> Path:
    return Path(prefix_dir) / 'drive_c/windows/system32'


def _cache_dir() -> Path:
    return config.path.cache_dir / 'optiscaler'


def _manifest_path(compat_dir: str) -> Path:
    return _managed_dir(compat_dir) / __manifest_file


def _load_manifest(compat_dir: str) -> dict:
    path = _manifest_path(compat_dir)
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
    path = _manifest_path(compat_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as fd:
        json.dump(manifest, fd, indent=2, sort_keys=True)
        fd.write('\n')


def _remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
    elif path.is_dir():
        shutil.rmtree(path)


def _set_env_list(env: dict, key: str, value: str, separator: str = ';') -> None:
    parts = [part for part in env.get(key, '').split(separator) if part]
    if value not in parts:
        parts.append(value)
    if parts:
        env[key] = separator.join(parts)
    elif key in env:
        del env[key]


def _drop_env_list(env: dict, key: str, value: str, separator: str = ';') -> None:
    parts = [part for part in env.get(key, '').split(separator) if part and part != value]
    if parts:
        env[key] = separator.join(parts)
    elif key in env:
        del env[key]


def _payload_root_value(compat_dir: str, payload_root: Path) -> str:
    try:
        return str(payload_root.relative_to(_managed_dir(compat_dir)))
    except ValueError:
        return str(payload_root)


def _payload_id(url: str) -> str:
    return hashlib.sha256(url.encode('utf-8')).hexdigest()[:12]


def _resolve_release() -> dict:
    return {
        'asset_name': __default_asset_name,
        'url': __default_url,
        'version': __default_version,
    }


def _resolve_payload_override(env: dict) -> Optional[Path]:
    payload_path = env.get(__path_var, '').strip()
    if not payload_path:
        return None

    payload_root = Path(payload_path).expanduser().resolve()
    if not payload_root.is_dir():
        raise RuntimeError(f'OptiScaler payload override is not a directory: "{payload_root}"')
    if not payload_root.joinpath(__main_dll).is_file():
        raise FileNotFoundError(f'OptiScaler payload override is missing "{__main_dll}"')
    return payload_root


def _find_payload_root(base_dir: Path) -> Path:
    candidates = sorted(
        {path.parent for path in base_dir.rglob(__main_dll) if path.is_file()},
        key=lambda path: (len(path.relative_to(base_dir).parts), str(path)),
    )
    if not candidates:
        raise FileNotFoundError(f'Unable to locate {__main_dll} in "{base_dir}"')
    return candidates[0]


def _payload_files(payload_root: Path) -> list[str]:
    return sorted(
        path.name
        for path in payload_root.glob('*.dll')
        if path.is_file() and path.name != __main_dll
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


def _ensure_payload(compat_dir: str, release: dict) -> tuple[Path, list[str]]:
    release_id = _payload_id(release['url'])
    payload_root = _managed_dir(compat_dir) / __payload_dir / f'{release["version"]}-{release_id}'
    if payload_root.joinpath(__main_dll).is_file():
        return payload_root, _payload_files(payload_root)

    archive_path = _cache_dir() / 'downloads' / f'{release_id}-{release["asset_name"]}'
    if not archive_path.is_file() or archive_path.stat().st_size == 0:
        log.info(f'Downloading OptiScaler from "{release["url"]}"')
        _download_file(release['url'], archive_path)

    log.info(f'Extracting OptiScaler "{archive_path.name}"')
    _extract_archive(archive_path, payload_root)
    return payload_root, _payload_files(payload_root)


def _managed_ini_path(compat_dir: str, payload_root: Path) -> Path:
    ini_path = _managed_dir(compat_dir) / __ini_file
    if ini_path.is_file():
        return ini_path

    payload_ini = payload_root / __ini_file
    if not payload_ini.is_file():
        raise FileNotFoundError(f'OptiScaler payload is missing "{__ini_file}"')

    ini_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(payload_ini, ini_path)
    return ini_path


def _parse_ini_overrides(config_value: str) -> list[tuple[str, str, str]]:
    overrides = []
    for entry in filter(None, (item.strip() for item in config_value.split(';'))):
        option_key, separator, value = entry.partition('=')
        section, dot, key = option_key.partition('.')
        if separator != '=' or dot != '.' or not section or not key:
            log.warn(f'Skipping invalid OptiScaler override "{entry}"')
            continue
        overrides.append((section, key, value))
    return overrides


def _patch_ini(lines: list[str], section: str, key: str, value: str) -> list[str]:
    header = f'[{section}]'
    start = next((i for i, line in enumerate(lines) if line.strip() == header), None)
    if start is None:
        if lines and lines[-1].strip():
            lines.append('')
        lines.extend((header, f'{key}={value}'))
        return lines

    end = next(
        (
            i
            for i in range(start + 1, len(lines))
            if lines[i].strip().startswith('[') and lines[i].strip().endswith(']')
        ),
        len(lines),
    )
    for i in range(start + 1, end):
        stripped = lines[i].strip()
        if not stripped or stripped.startswith((';', '#')):
            continue
        option, separator, _ = stripped.partition('=')
        if separator == '=' and option.strip() == key:
            lines[i] = f'{key}={value}'
            return lines

    lines.insert(end, f'{key}={value}')
    return lines


def _apply_ini_overrides(ini_path: Path, config_value: str) -> None:
    overrides = _parse_ini_overrides(config_value)
    if not overrides:
        return

    lines = ini_path.read_text(encoding='utf-8').splitlines()
    for section, key, value in overrides:
        lines = _patch_ini(lines, section, key, value)
    ini_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def _resolve_proxy(proxy: str, previous_proxy: str) -> str:
    proxy = proxy.strip().lower()
    if proxy in __true_values:
        proxy = 'auto'
    if proxy not in __supported_proxies:
        raise RuntimeError(f'Unsupported OptiScaler proxy "{proxy}"')
    if proxy != 'auto':
        return proxy
    return previous_proxy if previous_proxy in __auto_proxies else __auto_proxies[0]


def _stage_target(
    compat_dir: str,
    target: Path,
    previous_manifest: dict,
    *,
    managed: bool,
) -> None:
    backup = _managed_dir(compat_dir) / __backup_dir / target.name
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
    backup = _managed_dir(compat_dir) / __backup_dir / target.name
    _remove_path(target)
    if backup.exists() or backup.is_symlink():
        target.parent.mkdir(parents=True, exist_ok=True)
        backup.rename(target)


def _stage_proxy(prefix_dir: str, payload_root: Path, proxy: str, previous_manifest: dict) -> None:
    target = _system32_dir(prefix_dir) / f'{proxy}.dll'
    backup = _system32_dir(prefix_dir) / f'{proxy}-original.dll'

    if backup.exists() and previous_manifest.get('proxy') != proxy:
        raise RuntimeError(
            f'Cannot stage OptiScaler proxy "{proxy}" because "{backup.name}" already exists'
        )

    if target.exists() or target.is_symlink():
        if previous_manifest.get('enabled') and previous_manifest.get('proxy') == proxy:
            _remove_path(target)
        elif not backup.exists() and not backup.is_symlink():
            target.rename(backup)
        else:
            _remove_path(target)

    shutil.copy2(payload_root / __main_dll, target)


def _restore_proxy(prefix_dir: str, proxy: str) -> None:
    target = _system32_dir(prefix_dir) / f'{proxy}.dll'
    backup = _system32_dir(prefix_dir) / f'{proxy}-original.dll'
    _remove_path(target)
    if backup.exists() or backup.is_symlink():
        backup.rename(target)


def disable_optiscaler(compat_dir: str, prefix_dir: str, env: Optional[dict] = None) -> bool:
    """Restore the prefix to its stock state by removing OptiScaler staging."""
    manifest = _load_manifest(compat_dir)
    if not manifest.get('enabled'):
        return False

    system32 = _system32_dir(prefix_dir)
    for filename in (*manifest.get('payload_files', ()), __ini_file):
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
    env: dict,
    *,
    proxy: str = 'auto',
    config_value: str = '',
    payload_files: Optional[list[str]] = None,
) -> bool:
    """Stage a managed OptiScaler payload into the given game prefix."""
    previous_manifest = _load_manifest(compat_dir)
    payload_root = Path(payload_root)
    payload_files = payload_files or _payload_files(payload_root)
    resolved_proxy = _resolve_proxy(proxy, previous_manifest.get('proxy', ''))

    if previous_manifest.get('enabled') and (
        previous_manifest.get('proxy') != resolved_proxy
        or set(previous_manifest.get('payload_files', ())) != set(payload_files)
        or previous_manifest.get('payload_root') != _payload_root_value(compat_dir, payload_root)
    ):
        disable_optiscaler(compat_dir, prefix_dir, env)
        previous_manifest = _load_manifest(compat_dir)

    system32 = _system32_dir(prefix_dir)
    system32.mkdir(parents=True, exist_ok=True)
    managed_names = set(previous_manifest.get('payload_files', ())) | {__ini_file}

    ini_path = _managed_ini_path(compat_dir, payload_root)
    _apply_ini_overrides(ini_path, config_value)

    for filename in payload_files:
        target = system32 / filename
        _stage_target(compat_dir, target, previous_manifest, managed=filename in managed_names)
        target.symlink_to(Path(os.path.relpath(payload_root / filename, target.parent)))

    ini_target = system32 / __ini_file
    _stage_target(compat_dir, ini_target, previous_manifest, managed=True)
    ini_target.symlink_to(Path(os.path.relpath(ini_path, ini_target.parent)))

    _stage_proxy(prefix_dir, payload_root, resolved_proxy, previous_manifest)
    _set_env_list(env, 'WINEDLLOVERRIDES', f'{resolved_proxy}=n,b')

    manifest = dict(previous_manifest)
    manifest.update(
        {
            'enabled': True,
            'payload_files': payload_files,
            'payload_root': _payload_root_value(compat_dir, payload_root),
            'proxy': resolved_proxy,
        }
    )
    _save_manifest(compat_dir, manifest)
    log.info(f'Enabled OptiScaler with proxy "{resolved_proxy}".')
    return True


def setup_optiscaler(env: dict, compat_dir: str, prefix_dir: str) -> None:
    """Setup OptiScaler from Proton-style environment variables.

    usage: setup_optiscaler(g_session.env, g_compatdata.base_dir, g_compatdata.prefix_dir)
    """
    enabled = env.get(__env_var, '').strip()
    if not enabled:
        disable_optiscaler(compat_dir, prefix_dir, env)
        return

    try:
        payload_override = _resolve_payload_override(env)
        if payload_override is not None:
            payload_root = payload_override
            payload_files = _payload_files(payload_root)
        else:
            release = _resolve_release()
            payload_root, payload_files = _ensure_payload(compat_dir, release)
        enable_optiscaler(
            payload_root,
            compat_dir,
            prefix_dir,
            env,
            proxy='auto' if enabled.lower() in __true_values else enabled,
            config_value=env.get(__config_var, ''),
            payload_files=payload_files,
        )
    except (FileNotFoundError, RuntimeError, HTTPError, URLError, OSError) as exc:
        log.crit('Failed to setup OptiScaler.')
        log.crit(repr(exc))
