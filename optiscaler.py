"""Prefix-managed OptiScaler integration helpers."""

import configparser
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Optional

from . import util
from .logger import log


_MANAGED_DIR = 'optiscaler-managed'
_PAYLOAD_DIR = 'payload'
_BACKUP_DIR = 'backups'
_MANIFEST_FILE = 'manifest.json'
_INI_FILE = 'OptiScaler.ini'
_MAIN_DLL = 'OptiScaler.dll'
_TRUE_VALUES = {'1', 'true', 'yes', 'on', 'enable', 'enabled'}
_FALSE_VALUES = {'0', 'false', 'no', 'off', 'disable', 'disabled'}
_SUPPORTED_PROXIES = (
    'auto',
    'winmm',
    'dxgi',
    'version',
    'dbghelp',
    'winhttp',
    'wininet',
    'd3d12',
)
_AUTO_PROXIES = ('winmm', 'dxgi', 'version', 'dbghelp', 'winhttp', 'wininet', 'd3d12')
_PROFILE_OVERRIDES = {
    'default': (),
    'fsr4': (
        ('Upscalers', 'Dx12Upscaler', 'fsr31'),
        ('FSR', 'Fsr4ForceCapable', 'true'),
        ('FSR', 'Fsr4EnableWatermark', 'true'),
    ),
}


def _compat_dir() -> Path:
    compat_dir = os.environ.get('STEAM_COMPAT_DATA_PATH', '')
    if not compat_dir:
        raise RuntimeError('STEAM_COMPAT_DATA_PATH is not set')
    return Path(compat_dir)


def _prefix_dir() -> Path:
    return _compat_dir() / 'pfx'


def _system32_dir() -> Path:
    return _prefix_dir() / 'drive_c/windows/system32'


def _managed_dir() -> Path:
    return _compat_dir() / _MANAGED_DIR


def _payload_dir() -> Path:
    return _managed_dir() / _PAYLOAD_DIR


def _backup_dir() -> Path:
    return _managed_dir() / _BACKUP_DIR


def _manifest_path() -> Path:
    return _managed_dir() / _MANIFEST_FILE


def _load_manifest() -> dict:
    manifest_path = _manifest_path()
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


def _save_manifest(manifest: dict) -> None:
    managed_dir = _managed_dir()
    managed_dir.mkdir(parents=True, exist_ok=True)
    with _manifest_path().open('w', encoding='utf-8') as manifest_fd:
        json.dump(manifest, manifest_fd, indent=2, sort_keys=True)
        manifest_fd.write('\n')


def _remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
    elif path.is_dir():
        shutil.rmtree(path)


def _extract_payload(source: Path, destination: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(source)

    destination.parent.mkdir(parents=True, exist_ok=True)
    _remove_path(destination)

    with tempfile.TemporaryDirectory(prefix='optiscaler-payload-') as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        if source.is_dir():
            shutil.copytree(source, temp_dir / source.name, dirs_exist_ok=True)
        elif source.suffix.lower() == '.zip':
            with zipfile.ZipFile(source) as zip_fd:
                zip_fd.extractall(temp_dir)
        elif source.suffix.lower() == '.7z':
            binary = shutil.which('7z') or shutil.which('7zz')
            if binary is None:
                raise RuntimeError('7z archive support requires the 7z or 7zz binary in PATH')
            subprocess.run(
                [binary, 'x', str(source), f'-o{temp_dir}'],
                check=True,
                capture_output=True,
                text=True,
            )
        else:
            try:
                shutil.unpack_archive(str(source), str(temp_dir))
            except (shutil.ReadError, ValueError) as exc:
                raise RuntimeError(
                    f'Unsupported OptiScaler source "{source}". '
                    'Use a directory, .zip, or .7z archive.'
                ) from exc

        destination.mkdir(parents=True, exist_ok=True)
        for entry in temp_dir.iterdir():
            shutil.move(str(entry), destination / entry.name)


def _find_payload_root(base_dir: Path) -> Path:
    candidates = sorted(
        {path.parent for path in base_dir.rglob('*') if path.is_file() and path.name == _MAIN_DLL},
        key=lambda path: (len(path.relative_to(base_dir).parts), str(path)),
    )
    if not candidates:
        raise FileNotFoundError(f'Unable to locate {_MAIN_DLL} in "{base_dir}"')
    return candidates[0]


def _resolve_payload_root(source: Optional[str]) -> tuple[Path, str]:
    payload_dir = _payload_dir()
    manifest = _load_manifest()

    if source is not None:
        source_path = Path(source).expanduser().resolve()
        _extract_payload(source_path, payload_dir)
        payload_root = _find_payload_root(payload_dir)
        return payload_root, str(source_path)

    if manifest.get('payload_root'):
        payload_root = _managed_dir() / manifest['payload_root']
        if payload_root.is_dir() and payload_root.joinpath(_MAIN_DLL).is_file():
            return payload_root, manifest.get('source', '')

    if payload_dir.is_dir():
        payload_root = _find_payload_root(payload_dir)
        return payload_root, manifest.get('source', '')

    raise RuntimeError(
        'OptiScaler payload is not installed yet. '
        'Supply -pf_optiscaler=/path/to/payload first.'
    )


def _managed_ini_path(payload_root: Path) -> Path:
    ini_path = _managed_dir() / _INI_FILE
    if ini_path.exists():
        return ini_path

    payload_ini = payload_root / _INI_FILE
    _managed_dir().mkdir(parents=True, exist_ok=True)
    if payload_ini.is_file():
        shutil.copy2(payload_ini, ini_path)
    else:
        ini_path.write_text('; Generated by umu-protonfixes\n', encoding='utf-8')
    return ini_path


def _parse_ini_overrides(cfg: str) -> list[tuple[str, str, str]]:
    overrides = []
    for entry in filter(None, (item.strip() for item in cfg.split(';'))):
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


def _apply_ini_overrides(ini_path: Path, profile: str, cfg: str) -> None:
    profile = profile.lower()
    if profile not in _PROFILE_OVERRIDES:
        raise RuntimeError(f'Unsupported OptiScaler profile "{profile}"')

    overrides = list(_PROFILE_OVERRIDES[profile])
    overrides.extend(_parse_ini_overrides(cfg))
    if not overrides:
        return

    parser = configparser.RawConfigParser()
    parser.optionxform = str
    if ini_path.exists():
        parser.read(ini_path, encoding='utf-8')

    for section, key, value in overrides:
        if not parser.has_section(section):
            parser.add_section(section)
        parser.set(section, key, value)

    with ini_path.open('w', encoding='utf-8') as ini_fd:
        parser.write(ini_fd, space_around_delimiters=False)


def _resolve_proxy(proxy: str) -> str:
    proxy = proxy.lower()
    if proxy not in _SUPPORTED_PROXIES:
        raise RuntimeError(f'Unsupported OptiScaler proxy "{proxy}"')

    if proxy != 'auto':
        return proxy

    manifest = _load_manifest()
    previous_proxy = manifest.get('proxy', '')
    if previous_proxy in _AUTO_PROXIES:
        return previous_proxy

    return _AUTO_PROXIES[0]


def _stage_support_file(source: Path, target: Path) -> None:
    backup_path = _backup_dir() / target.name
    _backup_dir().mkdir(parents=True, exist_ok=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    manifest = _load_manifest()
    managed_files = set(manifest.get('staged_files', []))

    if target.exists() or target.is_symlink():
        if target.name in managed_files:
            _remove_path(target)
        elif not backup_path.exists() and not backup_path.is_symlink():
            target.rename(backup_path)
        else:
            _remove_path(target)

    target.symlink_to(Path(os.path.relpath(source, target.parent)))


def _restore_support_file(filename: str) -> None:
    target = _system32_dir() / filename
    backup_path = _backup_dir() / filename

    _remove_path(target)
    if backup_path.exists() or backup_path.is_symlink():
        target.parent.mkdir(parents=True, exist_ok=True)
        backup_path.rename(target)


def _stage_proxy(payload_root: Path, proxy: str) -> None:
    system32 = _system32_dir()
    system32.mkdir(parents=True, exist_ok=True)
    manifest = _load_manifest()

    target = system32 / f'{proxy}.dll'
    backup = system32 / f'{proxy}-original.dll'
    if backup.exists() and manifest.get('proxy') != proxy:
        raise RuntimeError(
            f'Cannot stage OptiScaler proxy "{proxy}" because "{backup.name}" already exists'
        )

    if target.exists() or target.is_symlink():
        if manifest.get('proxy') == proxy:
            _remove_path(target)
        elif not backup.exists() and not backup.is_symlink():
            target.rename(backup)
        else:
            _remove_path(target)

    shutil.copy2(payload_root / _MAIN_DLL, target)


def _restore_proxy(proxy: str) -> None:
    system32 = _system32_dir()
    target = system32 / f'{proxy}.dll'
    backup = system32 / f'{proxy}-original.dll'

    _remove_path(target)
    if backup.exists() or backup.is_symlink():
        backup.rename(target)


def disable_optiscaler() -> bool:
    manifest = _load_manifest()
    if not manifest:
        log.info('OptiScaler is not currently staged in this prefix.')
        return False

    for filename in manifest.get('staged_files', []):
        _restore_support_file(filename)

    proxy = manifest.get('proxy', '')
    if proxy:
        _restore_proxy(proxy)

    _manifest_path().unlink(missing_ok=True)
    log.info('Disabled OptiScaler for this prefix.')
    return True


def enable_optiscaler(
    source: Optional[str] = None,
    *,
    proxy: str = 'auto',
    profile: str = 'default',
    cfg: str = '',
) -> bool:
    payload_root, source_path = _resolve_payload_root(source)
    managed_ini = _managed_ini_path(payload_root)
    _apply_ini_overrides(managed_ini, profile, cfg)
    resolved_proxy = _resolve_proxy(proxy)

    previous_manifest = _load_manifest()
    if previous_manifest and previous_manifest.get('proxy') != resolved_proxy:
        disable_optiscaler()

    staged_files = []
    for dll_path in sorted(payload_root.glob('*.dll')):
        if dll_path.name == _MAIN_DLL:
            continue
        _stage_support_file(dll_path, _system32_dir() / dll_path.name)
        staged_files.append(dll_path.name)

    _stage_support_file(managed_ini, _system32_dir() / _INI_FILE)
    if _INI_FILE not in staged_files:
        staged_files.append(_INI_FILE)

    _stage_proxy(payload_root, resolved_proxy)
    util.winedll_override(resolved_proxy, util.OverrideOrder.NATIVE_BUILTIN)

    manifest = {
        'payload_root': str(payload_root.relative_to(_managed_dir())),
        'profile': profile.lower(),
        'proxy': resolved_proxy,
        'source': source_path,
        'staged_files': staged_files,
    }
    _save_manifest(manifest)
    log.info(f'Enabled OptiScaler with proxy "{resolved_proxy}".')
    return True


def handle_steam_launch_options(
    enabled: Optional[str],
    proxy: str = 'auto',
    profile: str = 'default',
    cfg: str = '',
) -> None:
    if enabled is None:
        return

    normalized = enabled.strip()
    lowered = normalized.lower()

    if lowered in _FALSE_VALUES:
        disable_optiscaler()
        return

    source = None if lowered in _TRUE_VALUES else normalized
    try:
        enable_optiscaler(source, proxy=proxy, profile=profile, cfg=cfg)
    except Exception as exc:
        log.crit('Failed to setup OptiScaler.')
        log.crit(repr(exc))
