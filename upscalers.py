"""Download and setup DLLs to upgrade various upscalers"""

import hashlib
import json
import os
import shutil
import urllib.request
import zipfile
from pathlib import Path
from typing import Callable, Union
from urllib.parse import unquote, urlparse

from .logger import log
from .config import config


__manifest_url = 'https://raw.githubusercontent.com/beeradmoore/dlss-swapper-manifest-builder/refs/heads/main/manifest.json'
__manifest_json: Union[dict, None] = None


def __get_manifest() -> dict:
    global __manifest_json
    if __manifest_json is not None:
        return __manifest_json

    cache_dir = config.path.cache_dir.joinpath('upscalers')
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached_manifest = cache_dir.joinpath('manifest.json')
    try:
        with urllib.request.urlopen(__manifest_url) as url_fd:
            __manifest_json = json.loads(url_fd.read())
        with cached_manifest.open('w') as manifest_fd:
            manifest_fd.write(json.dumps(__manifest_json))
    except Exception:
        if cached_manifest.exists():
            with cached_manifest.open() as manifest_fd:
                __manifest_json = json.loads(manifest_fd.read())

    return __manifest_json  # pyright: ignore [reportReturnType]


def __get_dll_manifest(upscaler: str, version: str = 'default') -> dict:
    dlls = __get_manifest()[upscaler]
    dlls = tuple(filter(lambda dll: not dll['is_dev_file'], dlls))
    for dll in reversed(dlls):
        if version in dll['version']:
            log.debug(f'Found "{upscaler.upper()}" dll version "{version}"')
            return dll
    log.debug(f'Version "{version}" for "{upscaler.upper()}" not found, using {dlls[-1]["version"]}')
    return dlls[-1]


__dlss_version_file = 'dlss_version'
__xess_version_file = 'xess_version'
__fsr3_version_file = 'fsr3_version'
__fsr4_version_file = 'fsr4_version'


def __get_dlss_dlls(version: str = 'default') -> dict:
    return {
        'drive_c/windows/system32/nvngx_dlss.dll': __get_dll_manifest('dlss', version),
        'drive_c/windows/system32/nvngx_dlssd.dll': __get_dll_manifest('dlss_d', version),
        'drive_c/windows/system32/nvngx_dlssg.dll': __get_dll_manifest('dlss_g', version),
    }


def __get_xess_dlls(version: str = 'default') -> dict:
    return {
        'drive_c/windows/system32/libxess.dll': __get_dll_manifest('xess', version),
        'drive_c/windows/system32/libxell.dll': __get_dll_manifest('xell', version),
        'drive_c/windows/system32/libxess_fg.dll': __get_dll_manifest('xess_fg', version),
    }


def __get_fsr3_dlls(version: str = 'default') -> dict:
    return {
        'drive_c/windows/system32/amd_fidelityfx_vk.dll': __get_dll_manifest('fsr_31_vk', version),
        'drive_c/windows/system32/amd_fidelityfx_dx12.dll': __get_dll_manifest('fsr_31_dx12', version),
    }


def __get_fsr4_dlls(version: str = 'default') -> dict:
    __fsr4_dlls = {
        '4.0.0': {
            'version': '4.0.0_67A4D2BC10ad000',
            'download_url': 'https://download.amd.com/dir/bin/amdxcffx64.dll/67A4D2BC10ad000/amdxcffx64.dll',
            'md5_hash': None,
            'zip_md5_hash': None,
        },
        '4.0.1': {
            'version': '4.0.1_67D435F7d97000',
            'download_url': 'https://download.amd.com/dir/bin/amdxcffx64.dll/67D435F7d97000/amdxcffx64.dll',
            'md5_hash': None,
            'zip_md5_hash': None,
        },
        '4.0.2': {
            'version': '4.0.2_68840348eb8000',
            'download_url': 'https://download.amd.com/dir/bin/amdxcffx64.dll/68840348eb8000/amdxcffx64.dll',
            'md5_hash': None,
            'zip_md5_hash': None,
        }
    }
    # use the safe option here for now
    if version == 'default' or version not in __fsr4_dlls.keys():
        version = '4.0.2'
    return {
        'drive_c/windows/system32/amdxcffx64.dll': __fsr4_dlls[version],
    }


def __check_upscaler_files(
    prefix_dir: str, files: dict, version_file: str, ignore_version: bool
) -> bool:
    if not os.path.isfile(version_file):
        log.warn(f'Missing version file "{version_file}"')
        return False

    try:
        with open(version_file) as version_fd:
            version = version_fd.read()
        version = json.loads(version)
        # test if new attributes as exist in the config
        _ = version[tuple(version.keys())[0]].get('md5_hash')
    except Exception as e:
        log.warn(f'Error while reading version file "{version_file}"')
        log.warn(str(e))
        return False

    for dst in files.keys():
        target = os.path.join(prefix_dir, dst)

        # Before everything, check if target is a symlink and remove it
        if os.path.islink(target):
            log.debug(f'Removing stale symlink "{dst}"')
            os.unlink(target)

        # First check if the file exists
        if not os.path.exists(target):
            log.warn(f'Missing file from prefix "{dst}"')
            return False

        with open(target, 'rb') as dst_fd:
            dst_md5 = hashlib.md5(dst_fd.read()).hexdigest().lower()

        # Then check if the file matches the one recorded in the version file
        version_md5 = version[dst]['md5_hash']
        if version_md5 is not None and dst_md5 != version_md5.lower():
            log.warn(f'MD5 checksum mismatch between version and prefix "{dst}"')
            return False

        # If we don't want to ignore the update
        # We ignore updates in the validation check after the downloads
        if not ignore_version:
            if version[dst]['version'] != files[dst]['version']:
                log.warn(f'Version mismatch between configuration and prefix "{dst}"')
                return False
            file_md5 = files[dst].get('md5_hash', None)
            if file_md5 is not None and dst_md5 != file_md5.lower():
                log.warn(f'MD5 checksum mismatch between manifest and prefix "{dst}"')
                return False
            log.debug(f'Found matching file in prefix "{dst}"')

    return True


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
    upscalers = {
        'dlss': (__get_dlss_dlls, __dlss_version_file),
        'xess': (__get_xess_dlls, __xess_version_file),
        'fsr3': (__get_fsr3_dlls, __fsr3_version_file),
        'fsr4': (__get_fsr4_dlls, __fsr4_version_file),
    }
    get_files, version_file = upscalers[name]
    try:
        files = get_files(version)
    except Exception:
        return False
    return __check_upscaler_files(
        prefix_dir, files, os.path.join(compat_dir, version_file), ignore_version,
    )


def __download_upscaler_files(
    prefix_dir: str, files: dict, dlfunc: Callable[[dict, Path, Path], None], version_file: str
) -> bool:
    """Download and install the required dlls.

    This function takes care of backing up, downloading, and installing the required dlls
    If the download fails, it will uses the backups to revert to the previous files, otherwise
    the backups are removed.

    The downloading, caching and installation of the dlls is facilitated in the callable passed through
    the `dlfunc` argument.
    """
    cache_dir = config.path.cache_dir.joinpath('upscalers')
    version = dict()
    for dst in files.keys():
        log.debug(f'Downloading upscaler file "{os.path.basename(dst)}"')
        file = Path(prefix_dir, dst)
        temp = Path(prefix_dir, dst + '.old')
        try:
            if file.exists():
                file.rename(temp)
            dlfunc(files[dst], cache_dir, file)
            if temp.exists():
                temp.unlink(missing_ok=True)
        except Exception as e:
            log.crit(f'Error while downloading file "{file.name}"')
            log.crit(str(e))
            if file.exists():
                file.unlink(missing_ok=True)
            if temp.exists():
                temp.rename(file)
            return False
        version[dst] = {'version': files[dst]['version'], 'md5_hash': files[dst]['md5_hash']}
    with open(version_file, 'w') as version_fd:
        version_fd.write(json.dumps(version))
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'
        },
    )
    try:
        with dst.open('wb') as dst_fd:
            dst_fd.write(urllib.request.urlopen(request, timeout=10).read())
        dst_md5 = hashlib.md5(dst.open('rb').read()).hexdigest().lower()
        if checksum is not None and dst_md5 != checksum.lower():
            raise RuntimeError(f'Malformed download {str(dst)}')
    except Exception as e:
        dst.unlink(missing_ok=True)
        raise e


def __download_extract_zip(file: dict, cache: Path, dst: Path) -> None:
    url_path = Path(unquote(urlparse(file['download_url']).path))
    cached_file = cache.joinpath(url_path.name)
    file_md5 = file.get('zip_md5_hash', None)
    if cached_file.exists():
        cached_md5 = hashlib.md5(cached_file.open('rb').read()).hexdigest().lower()
        if file_md5 is not None and cached_md5 != file_md5.lower():
            log.crit(f'MD5 checksum mismatch between manifest and cached "{cached_file.name}"')
            cached_file.unlink(missing_ok=True)
    if not cached_file.exists():
        __download_file(file['download_url'], cached_file, checksum=file_md5)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(cached_file) as zip_fd:
        zip_fd.extractall(dst.parent)


def __download_fsr4(file: dict, cache: Path, dst: Path) -> None:
    url_path = Path(unquote(urlparse(file['download_url']).path))
    cached_file = cache.joinpath(url_path.stem + f'_v{file["version"]}' + url_path.suffix)
    file_md5 = file.get('zip_md5_hash', None)
    if not cached_file.exists():
        __download_file(file['download_url'], cached_file, checksum=file_md5)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(cached_file, dst)


def download_upscaler(
    name: str, compat_dir: str, prefix_dir: str, version: str = 'default'
) -> None:
    """Check for upscaler files and their versions

    name: the name of the upscaler, possible values dlss, xess, fsr3, fsr4
    version: the version of the upscaler dll to download
    """
    if check_upscaler(name, compat_dir, prefix_dir, version, ignore_version=False):
        return
    else:
        log.info(f'Failed to validate "{name.upper()}" files.')

    upscalers = {
        'dlss': (__get_dlss_dlls, __download_extract_zip, __dlss_version_file),
        'xess': (__get_xess_dlls, __download_extract_zip, __xess_version_file),
        'fsr3': (__get_fsr3_dlls, __download_extract_zip, __fsr3_version_file),
        'fsr4': (__get_fsr4_dlls, __download_fsr4, __fsr4_version_file),
    }
    get_files, download_func, version_file = upscalers[name]
    try:
        files = get_files(version)
        if not __download_upscaler_files(
            prefix_dir, files, download_func, os.path.join(compat_dir, version_file),
        ):
            raise RuntimeError
    except Exception:
        log.warn(f'Failed to download {name.upper()} dlls.')


def __setup_upscaler(
    env: dict,
    key: str,
    name: str,
    compat_dir: str,
    prefix_dir: str,
    version: str = 'default',
) -> bool:
    version = env[key] if env.get(key, '0') not in {'0', '1'} else version
    download_upscaler(name, compat_dir, prefix_dir, version)
    enabled = check_upscaler(name, compat_dir, prefix_dir, version, ignore_version=True)
    if enabled:
        log.info(f'Automatic {name.upper()} upgrade enabled.')
    return enabled


def setup_upscalers(compat_config: set, env: dict, compat_dir: str, prefix_dir: str) -> None:
    """Setup configured upscalers

    usage: setup_upscalers(g_session.compat_config, g_session.env, g_compatdata.base_dir, g_compatdata.prefix_dir)
    """
    loaddll_replace = set()
    if 'dlss' in compat_config:
        if __setup_upscaler(env, 'PROTON_DLSS_UPGRADE', 'dlss', compat_dir, prefix_dir):
            loaddll_replace.add('dlss')
    if 'xess' in compat_config:
        if __setup_upscaler(env, 'PROTON_XESS_UPGRADE', 'xess', compat_dir, prefix_dir):
            loaddll_replace.add('xess')
    if 'fsr3' in compat_config:
        if __setup_upscaler(env, 'PROTON_FSR3_UPGRADE', 'fsr3', compat_dir, prefix_dir):
            loaddll_replace.add('fsr3')
    if 'fsr4rdna3' in compat_config:
        if __setup_upscaler(
            env, 'PROTON_FSR4_RDNA3_UPGRADE', 'fsr4', compat_dir, prefix_dir, '4.0.0'
        ):
            loaddll_replace.add('fsr4')
    elif 'fsr4' in compat_config:
        if __setup_upscaler(env, 'PROTON_FSR4_UPGRADE', 'fsr4', compat_dir, prefix_dir):
            loaddll_replace.add('fsr4')

    if 'fsr4' in loaddll_replace:
        force_enable_anti_lag = env.get('ENABLE_LAYER_MESA_ANTI_LAG', '0') != '1'
        env.setdefault('DISABLE_LAYER_MESA_ANTI_LAG', str(int(force_enable_anti_lag)))
        env['FSR4_UPGRADE'] = '1'
        if 'fsr4rdna3' in compat_config:
            env['DXIL_SPIRV_CONFIG'] = 'wmma_rdna3_workaround'

    if 'dlss' in loaddll_replace:
        env.setdefault(
            'DXVK_NVAPI_DRS_SETTINGS',
            str(
                'ngx_dlss_sr_override=on,'
                'ngx_dlss_rr_override=on,'
                'ngx_dlss_fg_override=on,'
                'ngx_dlss_sr_override_render_preset_selection=render_preset_latest,'
                'ngx_dlss_rr_override_render_preset_selection=render_preset_latest,'
            ),
        )

    if 'xess' in loaddll_replace:
        pass

    if 'fsr3' in loaddll_replace:
        pass

    if loaddll_replace:
        env['WINE_LOADDLL_REPLACE'] = ','.join(loaddll_replace)
