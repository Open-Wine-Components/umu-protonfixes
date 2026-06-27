"""Download and setup DLLs to upgrade various upscalers"""

import hashlib
import json
import lzma
import os
import shutil
import urllib.request
from functools import lru_cache
from urllib.error import HTTPError, URLError
import zipfile
from pathlib import Path
from typing import Callable, Union
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
        log.crit(e)
    else:
        with cached_manifest.open('w', encoding='utf-8') as manifest_fd:
            manifest_fd.write(json.dumps(__manifest_json))

    try:
        if not __manifest_json and cached_manifest.exists():
            with cached_manifest.open(encoding='utf-8') as manifest_fd:
                __manifest_json = json.loads(manifest_fd.read())
    except Exception as e:
        log.crit(f'Failed to read cached manifest "{str(cached_manifest)}"')
        log.crit(e)

    return __manifest_json  # pyright: ignore [reportReturnType]


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
__fsr3_section = 'fsr3_files'
__fsr4_section = 'fsr4_files'
__version_file = 'upscaler_files'


def __get_dlss_dlls(version: str = 'default') -> dict:
    return {
        'drive_c/windows/system32/umu/nvngx_dlss.dll': __get_dll_manifest('dlss', version),
        'drive_c/windows/system32/umu/nvngx_dlssd.dll': __get_dll_manifest(
            'dlss_d', version
        ),
        'drive_c/windows/system32/umu/nvngx_dlssg.dll': __get_dll_manifest(
            'dlss_g', version
        ),
    }


def __get_xess_dlls(version: str = 'default') -> dict:
    return {
        'drive_c/windows/system32/umu/libxess.dll': __get_dll_manifest('xess', version),
        'drive_c/windows/system32/umu/libxess_dx11.dll': __get_dll_manifest(
            'xess_dx11', version
        ),
        'drive_c/windows/system32/umu/libxell.dll': __get_dll_manifest('xell', version),
        'drive_c/windows/system32/umu/libxess_fg.dll': __get_dll_manifest(
            'xess_fg', version
        ),
    }


def __get_fsr3_dlls(version: str = 'default') -> dict:
    return {
        'drive_c/windows/system32/umu/amd_fidelityfx_vk.dll': __get_dll_manifest(
            'fsr_31_vk', version
        ),
        'drive_c/windows/system32/umu/amd_fidelityfx_dx12.dll': __get_dll_manifest(
            'fsr_31_dx12', version
        ),
    }


def __get_fsr4_dlls(version: str = 'default') -> dict:
    return {
        'drive_c/windows/system32/amdxcffx64.dll': __get_dll_manifest(
            'fsr_40_drv', version
        ),
    }


def __get_upscaler_items(name: str, version: str) -> tuple[dict, Callable, str]:
    upscalers = {
        'dlss': (__get_dlss_dlls, __download_extract_zip, __dlss_section),
        'xess': (__get_xess_dlls, __download_extract_zip, __xess_section),
        'fsr3': (__get_fsr3_dlls, __download_extract_zip, __fsr3_section),
        'fsr4': (__get_fsr4_dlls, __download_extract_zip, __fsr4_section),
    }
    get_items, dlfunc, section = upscalers[name]
    try:
        items = get_items(version)
    except Exception as e:
        log.crit(f'Failed to get "{name}" versions from manifest')
        log.crit(e)
        raise e

    return items, dlfunc, section


def __get_tracked_items(compat_dir: str, section: str) -> dict:
    tracking_file = os.path.join(compat_dir, __version_file)
    try:
        with open(tracking_file, encoding='utf-8') as file_fd:
            data = file_fd.read()
        tracked_versions = json.loads(data)
        tracked_versions = tracked_versions[section]
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
    prefix_dir: str, dst: str, remote_item: dict, tracked_item: dict, ignore_version: bool
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
    tracked_md5 = tracked_item['md5_hash']
    if tracked_md5 and dst_md5 != tracked_md5.lower():
        log.warn(f'MD5 checksum mismatch between tracking file and prefix "{dst}"')
        return False

    # If we don't want to ignore the update
    # We ignore updates in the validation check after the downloads
    if not ignore_version:
        if tracked_item['version'] != remote_item['version']:
            log.warn(f'Version mismatch between tracking file and prefix "{dst}"')
            return False
        item_md5 = remote_item.get('md5_hash', '')
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
        log.warn(e)
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
        items, _, section = __get_upscaler_items(name, version)
    except Exception:
        return False

    return __check_upscaler_files(
        compat_dir,
        prefix_dir,
        items,
        section,
        ignore_version,
    )


def __download_upscaler_files(
    compat_dir: str,
    prefix_dir: str,
    items: dict,
    dlfunc: Callable[[dict, Path, Path], None],
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
            dlfunc(items[dst], cache_dir, file)
            temp.unlink(missing_ok=True)
        except Exception as e:
            log.crit(f'Error while downloading file "{file.name}"')
            log.crit(e)
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


def download_upscaler(
    name: str, compat_dir: str, prefix_dir: str, version: str = 'default'
) -> None:
    """Check for upscaler files and their versions

    name: the name of the upscaler, possible values dlss, xess, fsr3, fsr4
    version: the version of the upscaler dll to download
    """
    if check_upscaler(name, compat_dir, prefix_dir, version, ignore_version=False):
        return
    log.info(f'Failed to validate "{name.upper()}" files.')

    try:
        items, download_func, section = __get_upscaler_items(name, version)
        if not __download_upscaler_files(
            compat_dir,
            prefix_dir,
            items,
            download_func,
            section,
        ):
            raise RuntimeError
    except Exception as e:
        log.crit(f'Failed to download {name.upper()} dlls.')
        log.crit(e)


def setup_upscaler(
    name: str,
    compat_dir: str,
    prefix_dir: str,
    version: str,
) -> bool:
    log.info(f'Setting up {name.upper()} version {version}.')
    download_upscaler(name, compat_dir, prefix_dir, version)
    enabled = check_upscaler(name, compat_dir, prefix_dir, version, ignore_version=True)
    return enabled


def get_version(env: dict, key: str, fallback: str) -> str:
    return env[key] if env.get(key, '0') not in {'0', '1'} else fallback


def setup_upscalers(
    compat_config: set, env: dict, compat_dir: str, prefix_dir: str
) -> None:
    """Setup configured upscalers

    usage: setup_upscalers(g_session.compat_config, g_session.env, g_compatdata.base_dir, g_compatdata.prefix_dir)
    """
    dlss_version = get_version(env, 'PROTON_DLSS_UPGRADE', 'default')
    xess_version = get_version(env, 'PROTON_XESS_UPGRADE', 'default')
    fsr3_version = get_version(env, 'PROTON_FSR3_UPGRADE', '1.0.1.41314')
    fsr4rdna3_version = get_version(env, 'PROTON_FSR4_RDNA3_UPGRADE', '4.0.0')
    fsr4_version = get_version(env, 'PROTON_FSR4_UPGRADE', 'default')
    fsr4_version = fsr4rdna3_version if 'fsr4rdna3' in compat_config else fsr4_version

    upscaler_replace = set()
    upscalers = (
        ('dlss', dlss_version, 'dlss' in compat_config),
        ('xess', xess_version, 'xess' in compat_config),
        ('fsr3', fsr3_version, 'fsr3' in compat_config),
        ('fsr4', fsr4_version, 'fsr4' in compat_config or 'fsr4rdna3' in compat_config),
    )
    for upscaler in upscalers:
        name, version, enabled = upscaler
        if enabled and setup_upscaler(name, compat_dir, prefix_dir, version):
            log.info(f'Automatic {name.upper()} upgrade enabled.')
            upscaler_replace.add(name)

    if 'fsr4' in upscaler_replace:
        env['FSR4_UPGRADE'] = '1'
        if 'mlfg' in compat_config:
            env['MLFG_UPGRADE'] = '1'
        if 'fsr4rdna3' in compat_config:
            env['DXIL_SPIRV_CONFIG'] = 'wmma_rdna3_workaround'

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

    if 'fsr3' in upscaler_replace:
        pass

    if upscaler_replace:
        env['WINE_UPSCALER_REPLACE'] = ','.join(upscaler_replace)
        log.debug(f'WINE_UPSCALER_REPLACE: {env["WINE_UPSCALER_REPLACE"]}.')



__all__ = ['setup_upscalers']
