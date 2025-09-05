"""Various utility functions for use in the proton script"""

import io
import json
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path
from typing import Callable, Union

from .logger import log
from .config import config


def winetricks(env: dict, wine_bin: str, wineserver_bin: str) -> None:
    """Handle winetricks"""
    if (
        env.get('UMU_ID')
        and env.get('EXE', '').endswith('winetricks')
        and env.get('PROTON_VERB') == 'waitforexitandrun'
    ):
        wt_verbs = ' '.join(sys.argv[2:][2:])
        env['WINE'] = wine_bin
        env['WINELOADER'] = wine_bin
        env['WINESERVER'] = wineserver_bin
        env['WINETRICKS_LATEST_VERSION_CHECK'] = 'disabled'
        env['LD_PRELOAD'] = ''

        log(f'Running winetricks verbs in prefix: {wt_verbs}')
        rc = subprocess.run(sys.argv[2:], check=False, env=env).returncode

        sys.exit(rc)


def _is_directory_empty(dir_path: str) -> bool:
    """Check if the directory is empty."""
    return not any(os.scandir(dir_path))


def setup_mount_drives(func: Callable[[str, str, str], None]) -> None:
    """Set up mount point drives for proton."""
    if os.environ.get('UMU_ID', ''):
        drive_map = {
            '/media': 'u:',
            '/run/media': 'v:',
            '/mnt': 'w:',
            os.path.expanduser('~'): 'x:',  # Current user's home directory
        }

        for directory in drive_map.keys():
            if os.access(directory, os.R_OK) and not _is_directory_empty(directory):
                func('gamedrive', drive_map[directory], directory)


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
    for dll in reversed(dlls):
        if version in dll['version']:
            return dll
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
            'version': '67A4D2BC10ad000',
            'download_url': 'https://download.amd.com/dir/bin/amdxcffx64.dll/67A4D2BC10ad000/amdxcffx64.dll',
        },
        '4.0.1': {
            'version': '67D435F7d97000',
            'download_url': 'https://download.amd.com/dir/bin/amdxcffx64.dll/67D435F7d97000/amdxcffx64.dll',
        },
        "4.0.2": {
            "version": '68840348eb8000',
            "download_url": 'https://download.amd.com/dir/bin/amdxcffx64.dll/68840348eb8000/amdxcffx64.dll',
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
        return False

    try:
        with open(version_file) as version_fd:
            version = version_fd.read()
        version = json.loads(version)
    except Exception as e:
        log.crit(str(e))
        return False

    for dst in files.keys():
        if not os.path.exists(os.path.join(prefix_dir, dst)):
            return False
        if ignore_version or version[dst] == files[dst]['version']:
            return True

    return False


def check_upscaler(
    name: str,
    compat_dir: str,
    prefix_dir: str,
    version: str = 'default',
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
    prefix_dir: str, files: dict, dlfunc: Callable[[str, str], None], version_file: str
) -> bool:
    cache_dir = config.path.cache_dir.joinpath('upscalers')
    version = dict()
    for dst in files.keys():
        file = Path(prefix_dir, dst)
        temp = Path(prefix_dir, dst + '.old')
        try:
            if file.exists():
                file.rename(temp)
            cached_file = cache_dir.joinpath(file.stem, files[dst]['version'], file.name)
            if not cached_file.exists():
                cached_file.parent.mkdir(parents=True, exist_ok=True)
                dlfunc(files[dst]['download_url'], cached_file.as_posix())
            shutil.copy(cached_file, file)
            if temp.exists():
                temp.unlink(missing_ok=True)
        except Exception as e:
            log.crit(str(e))
            if file.exists():
                file.unlink(missing_ok=True)
            if temp.exists():
                temp.rename(file)
            return False
        version[dst] = files[dst]['version']
    with open(version_file, 'w') as version_fd:
        version_fd.write(json.dumps(version))
    return True


def __download_extract_zip(url: str, dst: str) -> None:
    request = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'
        },
    )
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(request).read())) as zip_fd:
        zip_fd.extractall(os.path.dirname(dst))


def __download_fsr4(url: str, dst: str) -> None:
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    urllib.request.urlretrieve(url, dst)


def download_upscaler(
    name: str, compat_dir: str, prefix_dir: str, version: str = 'default'
) -> None:
    """Check for upscaler files and their versions

    name: the name of the upscaler, possible values dlss, xess, fsr3, fsr4
    version: the version of the upscaler dll to download
    """
    if check_upscaler(name, compat_dir, prefix_dir, version):
        return

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


def setup_upscalers(
    compat_config: set, env: dict, compat_dir: str, prefix_dir: str
) -> set:
    """Setup configured upscalers

    usage: setup_upscalers(g_session.compat_config, g_session.env, g_compatdata.base_dir, g_compatdata.prefix_dir)
    return: a set of the upscalers that have been successfully enabled
    """
    loaddll_replace = set()
    if 'dlss' in compat_config:
        if __setup_upscaler(env, 'PROTON_DLSS_UPGRADE', 'dlss', compat_dir, prefix_dir):
            loaddll_replace.add('dlss')
    if 'xess' in compat_config:
        if __setup_upscaler(env, 'PROTON_XESS_UPGRADE', 'xess', compat_dir, prefix_dir):
            loaddll_replace.add('xess')
    if 'fsr3' in compat_config:
        if __setup_upscaler(env, 'PROTON_XESS_UPGRADE', 'fsr3', compat_dir, prefix_dir):
            loaddll_replace.add('fsr3')
    if 'fsr4rdna3' in compat_config:
        if __setup_upscaler(
            env, 'PROTON_FSR4_RDNA3_UPGRADE', 'fsr4', compat_dir, prefix_dir, '4.0.0'
        ):
            loaddll_replace.add('fsr4')
    elif 'fsr4' in compat_config:
        if __setup_upscaler(env, 'PROTON_FSR4_UPGRADE', 'fsr4', compat_dir, prefix_dir):
            loaddll_replace.add('fsr4')
    if loaddll_replace:
        env['WINE_LOADDLL_REPLACE'] = ','.join(loaddll_replace)
    return loaddll_replace


def setup_local_shader_cache(env: dict) -> None:
    """Setup per-game shader cache if shader pre-caching is disabled

    usage: setup_local_shader_cache(g_session.env)
    """
    path = os.environ.get('STEAM_COMPAT_SHADER_PATH', '')
    if not path:
        return
    shader_cache_name = 'steamapp_shader_cache'
    shader_cache_vars = {
        # Nvidia
        '__GL_SHADER_DISK_CACHE_APP_NAME': shader_cache_name,
        '__GL_SHADER_DISK_CACHE_PATH': os.path.join(path, 'nvidiav1'),
        '__GL_SHADER_DISK_CACHE_READ_ONLY_APP_NAME': 'steam_shader_cache;steamapp_merged_shader_cache',
        '__GL_SHADER_DISK_CACHE_SIZE': '10737418240',  # 10GiB
        '__GL_SHADER_DISK_CACHE_SKIP_CLEANUP': '1',
        # Mesa
        'MESA_DISK_CACHE_READ_ONLY_FOZ_DBS': 'steam_cache,steam_precompiled',
        'MESA_DISK_CACHE_SINGLE_FILE': '1',
        'MESA_GLSL_CACHE_DIR': path,
        'MESA_GLSL_CACHE_MAX_SIZE': '5G',
        'MESA_SHADER_CACHE_DIR': path,
        'MESA_SHADER_CACHE_MAX_SIZE': '5G',
        # AMD VK
        'AMD_VK_PIPELINE_CACHE_FILENAME': shader_cache_name,
        'AMD_VK_PIPELINE_CACHE_PATH': os.path.join(path, 'AMDv1'),
        'AMD_VK_USE_PIPELINE_CACHE': '1',
        # DXVK
        'DXVK_STATE_CACHE_PATH': os.path.join(path, 'DXVK_state_cache'),
        # VKD3D
        'VKD3D_SHADER_CACHE_PATH': os.path.join(path, 'VKD3D_shader_cache'),
    }
    for var, val in shader_cache_vars.items():
        if var in os.environ:
            continue
        if var in {
            '__GL_SHADER_DISK_CACHE_PATH',
            'MESA_GLSL_CACHE_DIR',
            'MESA_SHADER_CACHE_DIR',
            'AMD_VK_PIPELINE_CACHE_PATH',
            'DXVK_STATE_CACHE_PATH',
            'VKD3D_SHADER_CACHE_PATH',
        }:
            os.makedirs(val, exist_ok=True)
        env[var] = val
