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
from urllib.parse import unquote, urlparse

from .config import config
from .logger import log


__managed_dir = 'optiscaler-managed'
__payload_dir = 'payload'
__backup_dir = 'backups'
__manifest_file = 'manifest.json'
__ini_file = 'OptiScaler.ini'
__main_dll = 'OptiScaler.dll'
__env_var = 'PROTON_OPTISCALER'
__url_var = 'PROTON_OPTISCALER_URL'
__config_var = 'PROTON_OPTISCALER_CONFIG'
__true_values = {'1', 'true', 'yes', 'on', 'enable', 'enabled'}
__false_values = {'0', 'false', 'no', 'off', 'disable', 'disabled'}
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
__release_api = 'https://api.github.com/repos/optiscaler/OptiScaler/releases/latest'
__default_version = '0.7.9'
__default_url = (
    'https://github.com/optiscaler/OptiScaler/releases/download/'
    f'v{__default_version}/OptiScaler_{__default_version}.7z'
)


def _managed_path(compat_dir: str) -> Path:
    return Path(compat_dir) / __managed_dir


def _payload_path(compat_dir: str) -> Path:
    return _managed_path(compat_dir) / __payload_dir


def _backup_path(compat_dir: str) -> Path:
    return _managed_path(compat_dir) / __backup_dir


def _manifest_path(compat_dir: str) -> Path:
    return _managed_path(compat_dir) / __manifest_file


def _system32_path(prefix_dir: str) -> Path:
    return Path(prefix_dir) / 'drive_c/windows/system32'


def _cache_dir() -> Path:
    return config.path.cache_dir.joinpath('optiscaler')


def _load_manifest(compat_dir: str) -> dict:
    manifest_path = _manifest_path(compat_dir)
    if not manifest_path.is_file():
        return {}

    try:
        with manifest_path.open(encoding='utf-8') as manifest_fd:
            manifest = json.load(manifest_fd)
        if isinstance(manifest, dict):
            return manifest
    except Exception as exc:
        log.warn(f'Failed to read OptiScaler manifest "{manifest_path}"')
        log.warn(repr(exc))

    return {}


def _save_manifest(compat_dir: str, manifest: dict) -> None:
    managed_dir = _managed_path(compat_dir)
    managed_dir.mkdir(parents=True, exist_ok=True)
    with _manifest_path(compat_dir).open('w', encoding='utf-8') as manifest_fd:
        json.dump(manifest, manifest_fd, indent=2, sort_keys=True)
        manifest_fd.write('\n')


def _remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
    elif path.is_dir():
        shutil.rmtree(path)


def _append_env(env: dict, key: str, value: str, separator: str = ';') -> None:
    parts = [part for part in env.get(key, '').split(separator) if part]
    if value not in parts:
        parts.append(value)
    if parts:
        env[key] = separator.join(parts)
    elif key in env:
        del env[key]


def _remove_env(env: dict, key: str, value: str, separator: str = ';') -> None:
    parts = [part for part in env.get(key, '').split(separator) if part and part != value]
    if parts:
        env[key] = separator.join(parts)
    elif key in env:
        del env[key]


def _payload_root_from_manifest(compat_dir: str, manifest: dict) -> Optional[Path]:
    payload_root = manifest.get('payload_root', '')
    if not payload_root:
        return None

    payload_path = Path(payload_root)
    if payload_path.is_absolute():
        return payload_path

    return _managed_path(compat_dir) / payload_root


def _payload_root_value(compat_dir: str, payload_root: Path) -> str:
    try:
        return str(payload_root.relative_to(_managed_path(compat_dir)))
    except ValueError:
        return str(payload_root)


def _find_payload_root(base_dir: Path) -> Path:
    candidates = sorted(
        {path.parent for path in base_dir.rglob('*') if path.is_file() and path.name == __main_dll},
        key=lambda path: (len(path.relative_to(base_dir).parts), str(path)),
    )
    if not candidates:
        raise FileNotFoundError(f'Unable to locate {__main_dll} in "{base_dir}"')
    return candidates[0]


def _payload_files(payload_root: Path) -> list[str]:
    return sorted(
        dll_path.name
        for dll_path in payload_root.glob('*.dll')
        if dll_path.is_file() and dll_path.name != __main_dll
    )


def _download_json(url: str, cache_path: Path) -> dict:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url,
        headers={
            'Accept': 'application/vnd.github+json',
            'User-Agent': 'umu-protonfixes',
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as url_fd:
            release = json.loads(url_fd.read())
    except Exception as exc:
        log.warn(f'Failed to fetch OptiScaler release metadata from "{url}"')
        log.warn(repr(exc))
        if cache_path.is_file():
            with cache_path.open(encoding='utf-8') as cache_fd:
                return json.load(cache_fd)
        return {}

    with cache_path.open('w', encoding='utf-8') as cache_fd:
        json.dump(release, cache_fd)
    return release


def _fallback_release() -> dict:
    return {
        'asset_name': Path(unquote(urlparse(__default_url).path)).name,
        'url': __default_url,
        'version': __default_version,
    }


def _release_from_api() -> dict:
    release = _download_json(
        __release_api,
        _cache_dir().joinpath('releases', 'latest.json'),
    )
    if not release:
        return _fallback_release()

    assets = tuple(
        asset for asset in release.get('assets', ()) if asset.get('name', '').endswith('.7z')
    )
    if not assets:
        log.warn('No OptiScaler .7z asset found in release metadata')
        return _fallback_release()

    asset = assets[0]
    return {
        'asset_name': asset['name'],
        'url': asset['browser_download_url'],
        'version': str(release.get('tag_name', '')).lstrip('v') or __default_version,
    }


def _release_from_url(url: str) -> dict:
    url_path = Path(unquote(urlparse(url).path))
    version = 'custom'
    name = url_path.name
    prefix = 'OptiScaler_'
    suffix = '.7z'
    if name.startswith(prefix) and name.endswith(suffix):
        version = name[len(prefix) : -len(suffix)]

    return {
        'asset_name': name or 'OptiScaler_custom.7z',
        'url': url,
        'version': version,
    }


def _resolve_release(env: dict, compat_dir: str) -> dict:
    manifest = _load_manifest(compat_dir)
    explicit_url = env.get(__url_var, '').strip()
    if explicit_url:
        return _release_from_url(explicit_url)

    payload_root = _payload_root_from_manifest(compat_dir, manifest)
    if (
        payload_root is not None
        and payload_root.joinpath(__main_dll).is_file()
        and manifest.get('url')
        and manifest.get('version')
    ):
        return {
            'asset_name': manifest.get('asset_name', ''),
            'url': manifest['url'],
            'version': manifest['version'],
        }

    return _release_from_api()


def _download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url,
        headers={'User-Agent': 'umu-protonfixes'},
    )
    with destination.open('wb') as destination_fd:
        with urllib.request.urlopen(request, timeout=30) as url_fd:
            shutil.copyfileobj(url_fd, destination_fd)


def _archive_path(release: dict) -> Path:
    release_id = hashlib.sha256(release['url'].encode('utf-8')).hexdigest()[:12]
    asset_name = release['asset_name'] or f'OptiScaler_{release["version"]}.7z'
    return _cache_dir().joinpath('downloads', f'{release_id}-{asset_name}')


def _payload_release_id(release: dict) -> str:
    release_id = hashlib.sha256(release['url'].encode('utf-8')).hexdigest()[:12]
    return f'{release["version"]}-{release_id}'


def _extract_archive(archive_path: Path, destination: Path) -> None:
    binary = shutil.which('7z') or shutil.which('7zz')
    if binary is None:
        raise RuntimeError('OptiScaler extraction requires the 7z or 7zz binary in PATH')

    destination.parent.mkdir(parents=True, exist_ok=True)
    _remove_path(destination)

    with tempfile.TemporaryDirectory(prefix='optiscaler-payload-') as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        subprocess.run(
            [binary, 'x', str(archive_path), f'-o{temp_dir}'],
            check=True,
            capture_output=True,
            text=True,
        )
        payload_root = _find_payload_root(temp_dir)
        shutil.copytree(payload_root, destination)


def _ensure_payload(compat_dir: str, release: dict) -> tuple[Path, list[str]]:
    payload_root = _payload_path(compat_dir) / _payload_release_id(release)
    if payload_root.joinpath(__main_dll).is_file():
        return payload_root, _payload_files(payload_root)

    archive_path = _archive_path(release)
    if not archive_path.is_file() or archive_path.stat().st_size == 0:
        log.info(f'Downloading OptiScaler from "{release["url"]}"')
        _download_file(release['url'], archive_path)

    log.info(f'Extracting OptiScaler "{archive_path.name}"')
    _extract_archive(archive_path, payload_root)
    return payload_root, _payload_files(payload_root)


def _managed_ini_path(compat_dir: str, payload_root: Path) -> Path:
    ini_path = _managed_path(compat_dir) / __ini_file
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
        if separator != '=':
            log.warn(f'Skipping invalid OptiScaler override "{entry}"')
            continue

        section, dot, key = option_key.partition('.')
        if dot != '.' or not section or not key:
            log.warn(f'Skipping invalid OptiScaler override "{entry}"')
            continue

        overrides.append((section, key, value))

    return overrides


def _patch_ini(lines: list[str], section: str, key: str, value: str) -> list[str]:
    section_header = f'[{section}]'
    section_start = None
    section_end = len(lines)

    for index, line in enumerate(lines):
        if line.strip() == section_header:
            section_start = index
            break

    if section_start is None:
        if lines and lines[-1].strip():
            lines.append('')
        lines.extend((section_header, f'{key}={value}'))
        return lines

    for index in range(section_start + 1, len(lines)):
        stripped = lines[index].strip()
        if stripped.startswith('[') and stripped.endswith(']'):
            section_end = index
            break

    for index in range(section_start + 1, section_end):
        stripped = lines[index].strip()
        if not stripped or stripped.startswith(';') or stripped.startswith('#'):
            continue
        option, separator, _ = stripped.partition('=')
        if separator == '=' and option.strip() == key:
            lines[index] = f'{key}={value}'
            return lines

    lines.insert(section_end, f'{key}={value}')
    return lines


def _apply_ini_overrides(ini_path: Path, config_value: str) -> None:
    overrides = _parse_ini_overrides(config_value)
    if not overrides:
        return

    lines = ini_path.read_text(encoding='utf-8').splitlines()
    for section, key, value in overrides:
        lines = _patch_ini(lines, section, key, value)

    ini_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def _resolve_proxy(proxy: str, manifest: dict) -> str:
    normalized = proxy.strip().lower()
    if normalized in __true_values:
        normalized = 'auto'
    if normalized not in __supported_proxies:
        raise RuntimeError(f'Unsupported OptiScaler proxy "{proxy}"')

    if normalized != 'auto':
        return normalized

    previous_proxy = manifest.get('proxy', '')
    if previous_proxy in __auto_proxies:
        return previous_proxy

    return __auto_proxies[0]


def _stage_support_file(
    compat_dir: str,
    filename: str,
    source: Path,
    target: Path,
    previous_manifest: dict,
) -> None:
    backup_path = _backup_path(compat_dir) / filename
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    managed_files = set(previous_manifest.get('payload_files', ()))
    managed_files.add(__ini_file)

    if target.exists() or target.is_symlink():
        if previous_manifest.get('enabled') and filename in managed_files:
            _remove_path(target)
        elif not backup_path.exists() and not backup_path.is_symlink():
            target.rename(backup_path)
        else:
            _remove_path(target)

    target.symlink_to(Path(os.path.relpath(source, target.parent)))


def _restore_support_file(compat_dir: str, prefix_dir: str, filename: str) -> None:
    target = _system32_path(prefix_dir) / filename
    backup_path = _backup_path(compat_dir) / filename

    _remove_path(target)
    if backup_path.exists() or backup_path.is_symlink():
        target.parent.mkdir(parents=True, exist_ok=True)
        backup_path.rename(target)


def _stage_proxy(payload_root: Path, prefix_dir: str, proxy: str, previous_manifest: dict) -> None:
    system32 = _system32_path(prefix_dir)
    system32.mkdir(parents=True, exist_ok=True)

    target = system32 / f'{proxy}.dll'
    backup = system32 / f'{proxy}-original.dll'

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
    system32 = _system32_path(prefix_dir)
    target = system32 / f'{proxy}.dll'
    backup = system32 / f'{proxy}-original.dll'

    _remove_path(target)
    if backup.exists() or backup.is_symlink():
        backup.rename(target)


def disable_optiscaler(
    compat_dir: str,
    prefix_dir: str,
    env: Optional[dict] = None,
) -> bool:
    manifest = _load_manifest(compat_dir)
    if not manifest.get('enabled'):
        return False

    for filename in manifest.get('payload_files', ()):
        _restore_support_file(compat_dir, prefix_dir, filename)
    _restore_support_file(compat_dir, prefix_dir, __ini_file)

    proxy = manifest.get('proxy', '')
    if proxy:
        _restore_proxy(prefix_dir, proxy)
        if env is not None:
            _remove_env(env, 'WINEDLLOVERRIDES', f'{proxy}=n,b')

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
    release: Optional[dict] = None,
    payload_files: Optional[list[str]] = None,
) -> bool:
    previous_manifest = _load_manifest(compat_dir)
    resolved_proxy = _resolve_proxy(proxy, previous_manifest)
    payload_root = Path(payload_root)
    payload_files = payload_files or _payload_files(payload_root)

    if previous_manifest.get('enabled') and (
        previous_manifest.get('proxy') != resolved_proxy
        or set(previous_manifest.get('payload_files', ())) != set(payload_files)
        or previous_manifest.get('payload_root') != _payload_root_value(compat_dir, payload_root)
    ):
        disable_optiscaler(compat_dir, prefix_dir, env)
        previous_manifest = _load_manifest(compat_dir)

    managed_ini = _managed_ini_path(compat_dir, payload_root)
    _apply_ini_overrides(managed_ini, config_value)

    for filename in payload_files:
        _stage_support_file(
            compat_dir,
            filename,
            payload_root / filename,
            _system32_path(prefix_dir) / filename,
            previous_manifest,
        )

    _stage_support_file(
        compat_dir,
        __ini_file,
        managed_ini,
        _system32_path(prefix_dir) / __ini_file,
        previous_manifest,
    )
    _stage_proxy(payload_root, prefix_dir, resolved_proxy, previous_manifest)
    _append_env(env, 'WINEDLLOVERRIDES', f'{resolved_proxy}=n,b')

    manifest = dict(previous_manifest)
    if release is not None:
        manifest.update(release)
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
    if not enabled or enabled.lower() in __false_values:
        disable_optiscaler(compat_dir, prefix_dir, env)
        return

    proxy = 'auto' if enabled.lower() in __true_values else enabled
    config_value = env.get(__config_var, '')

    try:
        release = _resolve_release(env, compat_dir)
        payload_root, payload_files = _ensure_payload(compat_dir, release)
        enable_optiscaler(
            payload_root,
            compat_dir,
            prefix_dir,
            env,
            proxy=proxy,
            config_value=config_value,
            release=release,
            payload_files=payload_files,
        )
    except (FileNotFoundError, RuntimeError, HTTPError, URLError, OSError) as exc:
        log.crit('Failed to setup OptiScaler.')
        log.crit(repr(exc))
