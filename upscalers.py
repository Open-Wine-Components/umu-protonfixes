"""Download and setup DLLs to upgrade various upscalers"""

import configparser
import hashlib
import json
import lzma
import os
import tarfile
import urllib.request
from functools import lru_cache
from urllib.error import HTTPError, URLError
import zipfile
from pathlib import Path
from typing import Union
from urllib.parse import unquote, urlparse

from .logger import log
from .config import config


__manifest_url = 'https://loathingkernel.github.io/proton-upscalers/manifest.json'
__manifest_json: Union[dict, None] = None


def __get_manifest() -> dict:
    global __manifest_json
    if __manifest_json is not None:
        return __manifest_json

    cache_dir = config.path.cache_dir.joinpath('upscalers')
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached_manifest = cache_dir.joinpath('manifest.json')
    __manifest_json = {}

    try:
        with urllib.request.urlopen(__manifest_url, timeout=10) as url_fd:
            __manifest_json = json.loads(url_fd.read())
    except Exception as e:
        log.crit(f'Failed to download "{__manifest_url}"')
        log.crit(str(e))
    else:
        with cached_manifest.open('w', encoding='utf-8') as manifest_fd:
            manifest_fd.write(json.dumps(__manifest_json))

    try:
        if not __manifest_json and cached_manifest.exists():
            with cached_manifest.open(encoding='utf-8') as manifest_fd:
                __manifest_json = json.loads(manifest_fd.read())
    except Exception as e:
        log.crit(f'Failed to read cached manifest "{str(cached_manifest)}"')
        log.crit(str(e))

    return __manifest_json  # pyright: ignore [reportReturnType]


@lru_cache(maxsize=16)
def __get_dll_manifest(upscaler: str, version: str = 'default') -> dict:
    dlls = __get_manifest()[upscaler]
    dlls = tuple(filter(lambda dll: not dll['is_dev_file'], dlls))
    for dll in reversed(dlls):
        if version in dll['version']:
            log.debug(f'Found "{upscaler.upper()}" dll version "{version}"')
            return dll
    log.debug(
        f'Version "{version}" for "{upscaler.upper()}" not found, using {dlls[-1]["version"]}'
    )
    return dlls[-1]


@lru_cache(maxsize=32)
def __get_dll_manifest_from_path(upscaler: str, path: Path) -> dict[str, Union[str , int , bool]]:
    file_size = path.stat().st_size
    with path.open("rb") as path_fd:
        file_md5_hash = hashlib.md5(path_fd.read()).hexdigest().upper()
    entry = {
        "version": "unknown",
        "download_url": str(path),
        "file_description": upscaler,
        "file_size": file_size,
        "zip_file_size": file_size,
        "is_dev_file": False,
        "is_bundle": False,
        "md5_hash": file_md5_hash,
        "zip_md5_hash": file_md5_hash,
    }
    return entry


@lru_cache(maxsize=32)
def __dll_download_exists(url: str) -> bool:
    try:
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=2) as response:
            if response.status == 200:
                log.info(f'Found reachable URL {url}')
                return True
    except (HTTPError, URLError, ValueError) as e:
        log.debug(f'URL {url} returned {e}')
    return False


__dlss_section = 'dlss_files'
__xess_section = 'xess_files'
__fsr4_section = 'fsr4_files'
__opti_section = 'opti_files'
__ffx3_section = 'ffx3_files'
__ffx4_section = 'ffx4_files'
__nvsl_section = 'nvsl_files'
__version_file = 'upscaler_files'


def __get_entry(filepath: str, group: str, version: str) -> dict[str, dict]:
    path = Path(version)
    __sys32 = 'drive_c/windows/system32'
    if path.is_absolute() and path.is_file():
        return {f'{__sys32}/{filepath}': __get_dll_manifest_from_path(group, path)}
    else:
        return {f'{__sys32}/{filepath}': __get_dll_manifest(group, version)}


def __get_entries(entries: tuple) -> dict:
    items: dict = {}
    for entry in entries:
        items.update(__get_entry(*entry))
    return items


def __get_opti_files(version: str = 'default') -> tuple[str, dict]:
    return 'drive_c/windows/system32/umu/', __get_dll_manifest('optiscaler', version)


def __get_nvsl_files(version: str = 'default') -> tuple[str, dict]:
    return 'drive_c/windows/system32/umu/streamline/', __get_dll_manifest('streamline', version)


def __get_dlss_dlls(version: str = 'default') -> dict[str, dict]:
    versions = version.split(':')
    if len(versions) != 3:
        versions = [version] * 3

    entries: tuple = (
        ('umu/nvngx_dlss.dll',  'dlss',   versions[0]),
        ('umu/nvngx_dlssd.dll', 'dlss_d', versions[1]),
        ('umu/nvngx_dlssg.dll', 'dlss_g', versions[2]),
    )
    return __get_entries(entries)


def __get_xess_dlls(version: str = 'default') -> dict[str, dict]:
    versions = version.split(':')
    if len(versions) != 4:
        versions = [version] * 4

    entries: tuple = (
        ('umu/libxess.dll',      'xess',      versions[0]),
        ('umu/libxess_dx11.dll', 'xess_dx11', versions[1]),
        ('umu/libxell.dll',      'xell',      versions[2]),
        ('umu/libxess_fg.dll',   'xess_fg',   versions[3]),
    )
    return __get_entries(entries)


def __get_ffx3_dlls(version: str = 'default') -> dict[str, dict]:
    versions = version.split(':')
    if len(versions) != 2:
        versions = [version] * 2

    entries: tuple = (
        ('umu/amd_fidelityfx_vk.dll',   'fsr_31_vk',   versions[0]),
        ('umu/amd_fidelityfx_dx12.dll', 'fsr_31_dx12', versions[1]),
    )
    return __get_entries(entries)


def __get_ffx4_dlls(version: str = 'default') -> dict[str, dict]:
    versions = version.split(':')
    if len(versions) != 3:
        versions = [version] * 3

    entries: tuple = (
        ('umu/amd_fidelityfx_framegeneration_dx12.dll', 'fsr_40_fg_dx12',  versions[0]),
        ('umu/amd_fidelityfx_loader_dx12.dll',          'fsr_40_ldr_dx12', versions[1]),
        ('umu/amd_fidelityfx_upscaler_dx12.dll',        'fsr_40_up_dx12',  versions[2]),
    )
    return __get_entries(entries)


def __get_fsr4_dlls(version: str = 'default') -> dict[str, dict]:
    versions = version.split(':')
    entries: tuple = (
        ('amdxcffx64.dll', 'fsr_40_drv', versions[0]),
    )
    return __get_entries(entries)


def __get_items(name: str, version: str) -> tuple[Union[dict[str, dict], tuple[str, dict]], str]:
    components = {
        'dlss': (__get_dlss_dlls, __dlss_section),
        'xess': (__get_xess_dlls, __xess_section),
        'fsr4': (__get_fsr4_dlls, __fsr4_section),
        'ffx3': (__get_ffx3_dlls, __ffx3_section),
        'ffx4': (__get_ffx4_dlls, __ffx4_section),
        'optiscaler': (__get_opti_files, __opti_section),
        'streamline': (__get_nvsl_files, __nvsl_section),
    }
    get_items, section = components[name]
    try:
        items = get_items(version)
    except Exception as e:
        log.crit(f'Failed to get "{name}" versions from manifest')
        log.crit(str(e))
        raise e

    return items, section


def __get_tracked_items(compat_dir: str, section: str) -> dict:
    tracking_file = os.path.join(compat_dir, __version_file)
    try:
        with open(tracking_file, encoding='utf-8') as file_fd:
            data = file_fd.read()
        tracked_versions = json.loads(data)
        tracked_versions = tracked_versions[section]
    except KeyError as e:
        log.warn(f'Section "{section}" not found in "{tracking_file}"')
        raise e
    except Exception as e:
        log.warn(f'Error while reading version file "{tracking_file}"')
        raise e

    return tracked_versions


def __set_tracked_items(compat_dir: str, section: str, checksums: dict) -> None:
    tracking_file = os.path.join(compat_dir, __version_file)
    try:
        with open(tracking_file, encoding='utf-8') as file_fd:
            data = file_fd.read()
        local_versions = json.loads(data)
    except Exception:
        log.warn(f'Error while reading version file "{tracking_file}"')
        local_versions = {}

    local_versions[section] = checksums

    with open(tracking_file, 'w', encoding='utf-8') as file_fd:
        file_fd.write(json.dumps(local_versions))


def __check_upscaler_file(
    prefix_dir: str, dst: str, remote: dict, tracked: dict, ignore_version: bool
) -> bool:
    target = os.path.join(prefix_dir, dst)

    # Before everything, check if target is a symlink
    # or the file size is unreasonably small and remove it
    if os.path.islink(target):
        log.debug(f'Removing stale symlink "{dst}"')
        os.unlink(target)
    if os.path.exists(target) and os.stat(target).st_size < 1024:
        log.debug(f'Removing stale file "{dst}"')
        os.unlink(target)

    # First check if the file exists
    if not os.path.exists(target):
        log.warn(f'Missing file from prefix "{dst}"')
        return False

    with open(target, 'rb') as dst_fd:
        dst_md5 = hashlib.md5(dst_fd.read()).hexdigest().lower()

    # Then check if the file matches the one recorded in the tracking file
    tracked_md5 = tracked['md5_hash']
    if tracked_md5 and dst_md5 != tracked_md5.lower():
        log.warn(f'MD5 checksum mismatch between tracking file and prefix "{dst}"')
        return False

    # If we don't want to ignore the update
    # We ignore updates in the validation check after the downloads
    if not ignore_version:
        if tracked['version'] != remote['version']:
            log.warn(f'Version mismatch between tracking file and prefix "{dst}"')
            return False
        item_md5 = remote.get('md5_hash', '')
        if item_md5 and dst_md5 != item_md5.lower():
            log.warn(f'MD5 checksum mismatch between manifest and prefix "{dst}"')
            return False
        log.debug(f'Found matching file in prefix "{dst}"')

    return True


def __check_upscaler_files(
    compat_dir: str, prefix_dir: str, remote_items: dict, section: str, ignore_version: bool
) -> bool:
    try:
        tracked_items = __get_tracked_items(compat_dir, section)
        # test if new files and their attributes exist in the tracking file
        for dst in remote_items.keys():
            _ = tracked_items[dst].get('md5_hash')
    except Exception as e:
        log.warn(str(e))
        return False

    valid_files = tuple(
        __check_upscaler_file(prefix_dir, dst, remote_items[dst], tracked_items[dst], ignore_version)
        for dst in remote_items.keys()
    )

    return all(valid_files)


def check_upscaler(
    name: str,
    compat_dir: str,
    prefix_dir: str,
    version: str = 'default',
    *,
    ignore_version: bool = False,
) -> bool:
    """Check for upscaler files and their versions

    name: the name of the upscaler, possible values dlss, xess, fsr3, fsr4
    version: the version of the upscaler dll to download
    ignore_version: ignore version mismatch but still check if the dlls are present
    """
    try:
        items, section = __get_items(name, version)
        if not isinstance(items, dict):
            raise RuntimeError(f'got return type {type(items).__name__}, expected dict')
    except Exception:
        return False

    return __check_upscaler_files(
        compat_dir,
        prefix_dir,
        items,
        section,
        ignore_version,
    )


def __check_component_files(
    compat_dir: str,
    prefix_dir: str,
    path: str,
    remote_item: dict,
    section: str,
    ignore_version: bool = False,
) -> bool:
    """Check for component files and its version

    version: the version of the component to download
    ignore_version: ignore version mismatch but still check if the files are present
    """
    try:
        tracked_items = __get_tracked_items(compat_dir, section)
        # test if new files and their attributes exist in the tracking file
        for dst in [os.path.join(path, f) for f in remote_item['md5_hash']]:
            _ = tracked_items[dst].get('md5_hash')
    except Exception as e:
        log.warn(str(e))
        return False

    dst_hashes = {}
    for dst in tracked_items:
        target = os.path.join(prefix_dir, dst)
        if not os.path.isfile(target):
            log.warn(f'Missing file from prefix "{dst}"')
            return False
        with open(target, 'rb') as dst_fd:
            dst_md5 = hashlib.md5(dst_fd.read()).hexdigest().lower()
        version_md5 = tracked_items[dst]['md5_hash']
        if version_md5 and dst_md5 != version_md5.lower():
            log.warn(f'MD5 checksum mismatch between version file and prefix "{dst}"')
            return False
        dst_hashes.update({dst: dst_md5})

    if not ignore_version:
        for name in remote_item['md5_hash']:
            dst = os.path.join(path, name)
            target = os.path.join(prefix_dir, dst)
            if not os.path.isfile(target):
                log.warn(f'Missing file from prefix "{dst}"')
                return False
            if tracked_items[dst]['version'] != remote_item['version']:
                log.warn(f'Version mismatch between configuration and prefix "{dst}"')
                return False
            item_md5 = remote_item['md5_hash'][name]
            if item_md5 and dst_hashes[dst] != item_md5.lower():
                log.warn(f'MD5 checksum mismatch between manifest and prefix "{dst}"')
                return False
            log.debug(f'Found matching file in prefix "{dst}"')

    return True


def check_component(
    name: str,
    compat_dir: str,
    prefix_dir: str,
    version: str = 'default',
    *,
    ignore_version: bool = False,
) -> bool:
    """Check for component files and their versions

    name: the name of the component, possible values optiscaler, streamline
    version: the version of the component to download
    ignore_version: ignore version mismatch but still check if the dlls are present
    """
    try:
        component, section = __get_items(name, version)
        if not isinstance(component, tuple):
            raise RuntimeError(f'got return type {type(component).__name__}, expected tuple')
        target_path, remote_item = component
    except Exception:
        return False

    return __check_component_files(
        compat_dir,
        prefix_dir,
        target_path,
        remote_item,
        section,
        ignore_version,
    )


def __download_file(url: str, dst: Path, *, checksum: Union[str, None] = None) -> None:
    """Downloads a file and checks against a checksum.

    If the download fails or the checksums do not match, the file is removed and the exception is
    propagated to the caller.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Proton/10.0'
        },
    )
    try:
        with dst.open('wb') as dst_fd:
            with urllib.request.urlopen(request, timeout=10) as url_fd:
                dst_fd.write(url_fd.read())
        with dst.open('rb') as dst_fd:
            dst_md5 = hashlib.md5(dst_fd.read()).hexdigest().lower()
        dst_size = dst.stat().st_size if dst.exists() else 0
        # Size check is arbitrary, but nothing should be below 1K
        if (checksum and dst_md5 != checksum.lower()) or dst_size < 1024:
            raise RuntimeError(f'Malformed download {str(dst)}')
    except Exception as e:
        dst.unlink(missing_ok=True)
        raise e


def __cached_download(item: dict, cached_file: Path) -> None:
    item_md5 = item.get('zip_md5_hash', '')

    if cached_file.exists():
        with cached_file.open('rb') as cached_fd:
            cached_md5 = hashlib.md5(cached_fd.read()).hexdigest().lower()
        if item_md5 and cached_md5 != item_md5.lower():
            log.crit(f'MD5 mismatch between manifest and cached "{cached_file.name}"')
            cached_file.unlink(missing_ok=True)

    if not cached_file.exists():
        __download_file(item['download_url'], cached_file, checksum=item_md5)


def __download_extract_zip(item: dict, cache: Path, dst: Path) -> None:
    url = item['download_url']
    if (not url.lower().startswith(('http://', 'https://'))) and Path(url).is_absolute():
        with Path(url).open('rb') as url_fd, dst.open('wb') as dst_fd:
            dst_fd.write(url_fd.read())
        return
    url_path = Path(unquote(urlparse(item['download_url']).path))
    cached_file = cache.joinpath(url_path.name)
    __cached_download(item, cached_file)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if cached_file.suffix == '.zip':
        with zipfile.ZipFile(cached_file) as zip_fd:
            zip_fd.extractall(dst.parent)
    if cached_file.suffix == '.xz':
        with dst.open('wb') as dst_fd:
            # this also sets the target filename
            with cached_file.open('rb') as cached_fd:
                dst_fd.write(lzma.decompress(cached_fd.read()))


def __download_upscaler_files(
    compat_dir: str,
    prefix_dir: str,
    items: dict,
    section: str,
) -> bool:
    """Download and install the required dlls.

    This function takes care of backing up, downloading, and installing the required dlls
    If the download fails, it will uses the backups to revert to the previous files, otherwise
    the backups are removed.

    The downloading, caching and installation of the dlls is facilitated in the callable passed through
    the `dlfunc` argument.
    """
    cache_dir = config.path.cache_dir.joinpath('upscalers')
    version = {}
    for dst in items.keys():
        log.info(f'Downloading upscaler file "{os.path.basename(dst)}"')
        file = Path(prefix_dir, dst)
        temp = Path(prefix_dir, dst + '.old')
        try:
            if file.exists() or file.is_symlink():
                file.rename(temp)
            __download_extract_zip(items[dst], cache_dir, file)
            temp.unlink(missing_ok=True)
        except Exception as e:
            log.crit(f'Error while downloading file "{file.name}"')
            log.crit(str(e))
            file.unlink(missing_ok=True)
            if temp.exists() or temp.is_symlink():
                temp.rename(file)
            return False
        version[dst] = {
            'version': items[dst]['version'],
            'md5_hash': items[dst]['md5_hash'],
        }
    __set_tracked_items(compat_dir, section, version)
    return True


def download_upscaler(
    name: str, compat_dir: str, prefix_dir: str, version: str = 'default'
) -> None:
    """Check for upscaler files and their versions

    name: the name of the upscaler, possible values dlss, xess, fsr3, fsr4
    version: the version of the upscaler dll to download
    """
    if check_upscaler(name, compat_dir, prefix_dir, version, ignore_version=False):
        return
    log.info(f'Failed to validate {name} files.')

    try:
        items, section = __get_items(name, version)
        if not isinstance(items, dict):
            raise RuntimeError(f'got return type {type(items).__name__}, expected dict')
        if not __download_upscaler_files(
            compat_dir,
            prefix_dir,
            items,
            section,
        ):
            raise RuntimeError
    except Exception as e:
        log.crit(f'Failed to download {name} dlls.')
        log.crit(str(e))


def __download_component_files(
    compat_dir: str,
    prefix_dir: str,
    path: str,
    item: dict,
    section: str,
) -> bool:
    """Check for optiscaler files and their versions

    version: the version of the upscaler dll to download
    """
    try:
        tracked_items = __get_tracked_items(compat_dir, section)
    except Exception:
        tracked_items = {}
        pass

    try:
        log.info(f'Updating {item["file_description"]} to "{item["version"]}"')

        url_path = Path(unquote(urlparse(item['download_url']).path))
        cache_dir = config.path.cache_dir.joinpath('upscalers')
        cache_dir.mkdir(parents=True, exist_ok=True)
        cached_file = cache_dir.joinpath(url_path.name)
        __cached_download(item, cached_file)

        for target in tracked_items:
            # do not remove .ini files
            if target.endswith('.ini'):
                continue
            local_file = os.path.join(prefix_dir, target)
            if os.path.exists(local_file):
                os.unlink(local_file)

        with tarfile.open(cached_file, 'r:xz') as tar_fd:
            names = tar_fd.getnames()
            for name in names:
                local_file = os.path.join(prefix_dir, path, name)
                if name.endswith('.ini') and os.path.exists(local_file):
                    os.rename(local_file, local_file + '.old' )
                tar_fd.extract(name, os.path.join(prefix_dir, path))

        version = {}
        for name in item['md5_hash']:
            version[os.path.join(path, name)] = {
                'version': item['version'],
                'md5_hash': item['md5_hash'][name]
            }

    except Exception as e:
        log.crit(f'Failed to download "{item["file_description"]}" package.')
        log.crit(str(e))
        return False

    __set_tracked_items(compat_dir, section, version)
    return True


def download_component(
    name: str, compat_dir: str, prefix_dir: str, version: str = 'default'
) -> None:
    """Check for upscaler files and their versions

    name: the name of the upscaler, possible values dlss, xess, fsr3, fsr4
    version: the version of the upscaler dll to download
    """
    if check_component(name, compat_dir, prefix_dir, version, ignore_version=False):
        return
    log.info(f'Failed to validate {name} files.')

    try:
        component, section = __get_items(name, version)
        if not isinstance(component, tuple):
            raise RuntimeError(f'got return type {type(component).__name__}, expected tuple')
        target_path, remote_item = component
        if not __download_component_files(
            compat_dir,
            prefix_dir,
            target_path,
            remote_item,
            section,
        ):
            raise RuntimeError
    except Exception as e:
        log.crit(f'Failed to download {name} files')
        log.crit(str(e))


def setup_upscaler(
    name: str,
    compat_dir: str,
    prefix_dir: str,
    version: str,
) -> bool:
    log.info(f'Setting up {name} version "{version}".')
    download_upscaler(name, compat_dir, prefix_dir, version)
    enabled = check_upscaler(name, compat_dir, prefix_dir, version, ignore_version=True)
    return enabled


def setup_optiscaler(
    env: dict,
    compat_dir: str,
    prefix_dir: str,
    version: str,
) -> bool:
    log.info(f'Setting up optiscaler version "{version}".')
    download_component("optiscaler", compat_dir, prefix_dir, version)
    enabled = check_component("optiscaler", compat_dir, prefix_dir, version, ignore_version=True)

    if enabled and env.get('PROTON_OPTISCALER_STREAMLINE', '0') != '0':
        streamline_version = get_version(env, 'PROTON_OPTISCALER_STREAMLINE', 'default')
        log.info(f'Setting up streamline version "{streamline_version}".')
        download_component("streamline", compat_dir, prefix_dir, streamline_version)
    else:
        clean_tracked_files('streamline', compat_dir, prefix_dir)

    if enabled and (env_config := env.get('PROTON_OPTISCALER_CONFIG', '')):
        path, _ = __get_opti_files(version)
        ini = os.path.join(prefix_dir, path, 'OptiScaler.ini')
        parser = configparser.ConfigParser()
        parser.read(ini)

        env_config_parts = env_config.split(';')
        env_config_parts = (part for part in env_config_parts if part)
        for part in env_config_parts:
            try:
                option_path, value = part.split('=')
                section, option = option_path.split('.')
            except Exception as e:
                log.crit(f'Malformed config "{part}"')
                log.debug(str(e))
                continue
            if section in parser and option in parser[section]:
                parser[section][option] = value
            else:
                log.warn(f'Ignoring unknown option "{f"{section}.{option}"}"')

        with open(ini, 'w') as ini_fd:
            parser.write(ini_fd)

    return enabled


def clean_tracked_files(
    name: str,
    compat_dir: str,
    prefix_dir: str,
) -> bool:
    try:
        _, section = __get_items(name, 'default')
    except Exception:
        return False

    log.info(f'Cleaning {name} files.')

    try:
        tracked_items = __get_tracked_items(compat_dir, section)
    except Exception:
        return False

    __set_tracked_items(compat_dir, section, {})

    for path in tracked_items:
        file = os.path.join(prefix_dir, path)
        if os.path.exists(file):
            log.debug(f'Removing {file}')
            os.unlink(file)

    return True


def get_version(env: dict, key: str, fallback: str) -> str:
    return env[key] if env.get(key, '0') not in {'0', '1'} else fallback


def check_upscalers_disabled() -> bool:
    """Determine if protonfixes upscalers have been explicitly disabled

    Returns:
        bool : True if upscaler installation is disabled from the environment
    """
    return 'PROTONFIXES_DISABLE_UPSCALERS' in os.environ and os.environ['PROTONFIXES_DISABLE_UPSCALERS'] != '0'


def setup_upscalers(
    compat_config: set, env: dict, compat_dir: str, prefix_dir: str
) -> None:
    """Setup configured upscalers

    usage: setup_upscalers(g_session.compat_config, g_session.env, g_compatdata.base_dir, g_compatdata.prefix_dir)
    """
    dlss_version: str = get_version(env, 'PROTON_DLSS_UPGRADE', 'default')
    xess_version: str = get_version(env, 'PROTON_XESS_UPGRADE', 'default')

    fsr4_version: str = get_version(env, 'PROTON_FSR4_UPGRADE', 'default')

    ffx3_version: str = get_version(env, 'PROTON_FFX3_UPGRADE', '1.0.1.41314')
    ffx4_version: str = get_version(env, 'PROTON_FFX4_UPGRADE', 'default')

    optiscaler_version = get_version(env, 'PROTON_USE_OPTISCALER', 'default')
    # if optiscaler is enabled, control ffx4_version through fsr4_version unless explicitly set
    if 'optiscaler' in compat_config and 'fsr4' in compat_config and 'ffx4' not in compat_config:
        ffx4_version = fsr4_version

    upscaler_replace = set()
    upscalers = (
        ('dlss', dlss_version, 'dlss' in compat_config or 'optiscaler' in compat_config),
        ('xess', xess_version, 'xess' in compat_config or 'optiscaler' in compat_config),
        # amdxcffx64 4.1.1
        ('fsr4', fsr4_version, 'fsr4' in compat_config or 'optiscaler' in compat_config),
        # fidelityfx sdk
        ('ffx3', ffx3_version, 'ffx3' in compat_config or 'optiscaler' in compat_config),
        ('ffx4', ffx4_version, 'ffx4' in compat_config),
    )
    for upscaler in upscalers:
        name, version, enabled = upscaler
        if enabled and setup_upscaler(name, compat_dir, prefix_dir, version):
            log.info(f'Automatic {name} upgrade enabled.')
            upscaler_replace.add(name)

    if 'optiscaler' in compat_config:
        if setup_optiscaler(env, compat_dir, prefix_dir, optiscaler_version):
            log.info('OptiScaler enabled.')
            if 'fsr4' in compat_config:
                if ffx4_version in {'4.0.0', '4.0.1'}:
                    clean_tracked_files('ffx4', compat_dir, prefix_dir)
                else:
                    setup_upscaler('ffx4', compat_dir, prefix_dir, ffx4_version)
            env['WINE_OPTISCALER_NAME'] = env.get('PROTON_OPTISCALER_NAME', 'dxgi.dll')
            upscaler_replace.clear()

    # let me explain...
    if 'fsr4' in upscaler_replace:
        # FSR4_UPGRADE is enabled by default on certain GPUs, under normal conditions we
        # do not want to force-enable it. If the user sets the PROTON_ env variable themselves
        # assume they know what they are doing and enable the extended GPU support for them.
        if env.get('PROTON_FSR4_UPGRADE') not in {'0', None}:
            env.setdefault('FSR4_UPGRADE', '1')
        if 'mlfg' in env:
            env.setdefault('MLFG_UPGRADE', '1')
    else:
        # At the same time if PROTON_FSR4_UPGRADE is set to '0', disable the upgrade, unless
        # the user has already set the FSR4_UPGRADE.
        env.setdefault('FSR4_UPGRADE', '0')
        env.setdefault('MLFG_UPGRADE', '0')

    if 'dlss' in upscaler_replace:
        env.setdefault(
            'DXVK_NVAPI_DRS_SETTINGS',
            'ngx_dlss_sr_override=on,'
            'ngx_dlss_rr_override=on,'
            'ngx_dlss_fg_override=on,'
            'ngx_dlss_sr_override_render_preset_selection=default,'
            'ngx_dlss_rr_override_render_preset_selection=default,',
        )

    if 'xess' in upscaler_replace:
        pass

    if 'ffx3' in upscaler_replace:
        pass

    if 'ffx4' in upscaler_replace:
        pass

    if upscaler_replace:
        env['WINE_UPSCALER_REPLACE'] = ','.join(upscaler_replace)
        log.debug(f'WINE_UPSCALER_REPLACE: {env["WINE_UPSCALER_REPLACE"]}.')


__all__ = [
    'check_upscalers_disabled',
    'setup_upscalers',
]
