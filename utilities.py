"""Various utility functions for use in the proton script"""

import io
import os
import subprocess
import sys
import urllib.request
import zipfile
from typing import Callable

from .logger import log


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


# DLSS, XeSS and FSR3 links taken from https://github.com/beeradmoore/dlss-swapper-manifest-builder/blob/main/manifest.json
__dlss_version = '310.3.0.0'
__dlss_version_file = 'dlss_version'
__dlss_urls = {
    'drive_c/windows/system32/nvngx_dlss.dll': 'https://dlss-swapper-downloads.beeradmoore.com/dlss/dlss_v310.3.0.0_436BD84602A538C63C4953F78B668204.zip',
    'drive_c/windows/system32/nvngx_dlssd.dll': 'https://dlss-swapper-downloads.beeradmoore.com/dlss_d/dlss_d_v310.3.0.0_FC7A45AFE0A8EFA3E9426C875F0CDF2B.zip',
    'drive_c/windows/system32/nvngx_dlssg.dll': 'https://dlss-swapper-downloads.beeradmoore.com/dlss_g/dlss_g_v310.3.0.0_ED5ACC14FFCBD33B0FAF2EAEFCC84F89.zip',
}
__xess_version = '2.1.0'
__xess_version_file = 'xess_version'
__xess_urls = {
    'drive_c/windows/system32/libxess.dll': 'https://dlss-swapper-downloads.beeradmoore.com/xess/xess_v2.0.2.53_B6D2A108369FE3CD7FC82AF14DD8C60C.zip',
    'drive_c/windows/system32/libxell.dll': 'https://dlss-swapper-downloads.beeradmoore.com/xell/xell_v1.2.0.9_7371177F39EFBBB60A3F1274244C3ECA.zip',
    'drive_c/windows/system32/libxess_fg.dll': 'https://dlss-swapper-downloads.beeradmoore.com/xess_fg/xess_fg_v1.2.0.87_904116C83B5C6115CBE41FF3BE513997.zip',
}
__fsr3_version = '1.0.1.41314'
__fsr3_version_file = 'fsr3_version'
__fsr3_urls = {
    'drive_c/windows/system32/amd_fidelityfx_vk.dll': 'https://dlss-swapper-downloads.beeradmoore.com/fsr_31_vk/fsr_31_vk_v1.0.1.41314_9718FD774C61BE1AF6AF411CF65394CD.zip',
    'drive_c/windows/system32/amd_fidelityfx_dx12.dll': 'https://dlss-swapper-downloads.beeradmoore.com/fsr_31_dx12/fsr_31_dx12_v1.0.1.41314_49230AD94ED6169933CD0457501D9CB4.zip',
}
__fsr4_version = '67A4D2BC10ad000'
__fsr4_version_file = 'fsr4_version'
__fsr4_urls = {
    'drive_c/windows/system32/amdxcffx64.dll': f'https://download.amd.com/dir/bin/amdxcffx64.dll/{__fsr4_version}/amdxcffx64.dll',
}


def __check_upscaler_files(prefix_dir: str, files: dict, version: str, version_file: str) -> bool:
    for dst in files.keys():
        if not os.path.exists(prefix_dir + dst):
            return False

    if not os.path.isfile(version_file):
        return False
    with open(version_file) as version_fd:
        old_version = version_fd.read()
    if old_version == version:
        return True

    return False


def check_dlss(compat_dir: str, prefix_dir: str) -> bool:
    """Setup if DLSS dlls are present and up-to-date

    usage: check_dlss(g_compatdata.base_dir, g_compatdata.prefix_dir)
    """
    return __check_upscaler_files(
        prefix_dir,
        __dlss_urls,
        __dlss_version,
        os.path.join(compat_dir, __dlss_version_file),
    )


def check_xess(compat_dir: str, prefix_dir: str) -> bool:
    """Setup if XeSS dlls are present and up-to-date

    usage: check_xess(g_compatdata.base_dir, g_compatdata.prefix_dir)
    """
    return __check_upscaler_files(
        prefix_dir,
        __xess_urls,
        __xess_version,
        os.path.join(compat_dir, __xess_version_file),
    )


def check_fsr3(compat_dir: str, prefix_dir: str) -> bool:
    """Setup if FSR3 dlls are present and up-to-date

    usage: check_fsr3(g_compatdata.base_dir, g_compatdata.prefix_dir)
    """
    return __check_upscaler_files(
        prefix_dir,
        __fsr3_urls,
        __fsr3_version,
        os.path.join(compat_dir, __fsr3_version_file),
    )


def check_fsr4(compat_dir: str, prefix_dir: str) -> bool:
    """Setup if FSR4 dlls are present and up-to-date

    usage: check_fsr4(g_compatdata.base_dir, g_compatdata.prefix_dir)
    """
    return __check_upscaler_files(
        prefix_dir,
        __fsr4_urls,
        __fsr4_version,
        os.path.join(compat_dir, __fsr4_version_file),
    )


def __setup_upscaler_files(prefix_dir: str, files: dict, dlfunc: Callable[[str, str], None], version: str, version_file: str) -> bool:
    for dst in files.keys():
        try:
            dlfunc(files[dst], prefix_dir + dst)
        except Exception:
            if os.path.exists(prefix_dir + dst):
                os.unlink(prefix_dir + dst)
            return False
    with open(version_file, 'w') as version_fd:
        version_fd.write(version)
    return True


def __download_extract_zip(url: str, dst: str) -> None:
    request = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'
        },
    )
    with zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(request).read())) as zip_fd:
        zip_fd.extractall(os.path.dirname(dst))


def setup_dlss(compat_dir: str, prefix_dir: str) -> None:
    """Setup DLSS

    usage: setup_dlss(g_compatdata.base_dir, g_compatdata.prefix_dir)
    """
    if check_dlss(compat_dir, prefix_dir):
        return
    if __setup_upscaler_files(
        prefix_dir,
        __dlss_urls,
        __download_extract_zip,
        __dlss_version,
        os.path.join(compat_dir, __dlss_version_file),
    ):
        log.info('Automatic DLSS upgrade enabled')
    else:
        log.warn('Failed to download nvngx_dlss*.dll')


def setup_xess(compat_dir: str, prefix_dir: str) -> None:
    """Setup XeSS

    usage: setup_xess(g_compatdata.base_dir, g_compatdata.prefix_dir)
    """
    if check_xess(compat_dir, prefix_dir):
        return
    if __setup_upscaler_files(
        prefix_dir,
        __xess_urls,
        __download_extract_zip,
        __xess_version,
        os.path.join(compat_dir, __xess_version_file),
    ):
        log.info('Automatic XeSS upgrade enabled')
    else:
        log.warn('Failed to download libxe*.dll')


def setup_fsr3(compat_dir: str, prefix_dir: str) -> None:
    """Setup FSR3

    usage: setup_fsr3(g_compatdata.base_dir, g_compatdata.prefix_dir)
    """
    if check_fsr3(compat_dir, prefix_dir):
        return
    if __setup_upscaler_files(
        prefix_dir,
        __fsr3_urls,
        __download_extract_zip,
        __fsr3_version,
        os.path.join(compat_dir, __fsr3_version_file),
    ):
        log.info('Automatic XeSS upgrade enabled')
    else:
        log.warn('Failed to download libxe*.dll')


def setup_fsr4(compat_dir: str, prefix_dir: str) -> None:
    """Setup FSR4

    usage: setup_fsr4(g_compatdata.base_dir, g_compatdata.prefix_dir)
    """
    if check_fsr4(compat_dir, prefix_dir):
        return

    def __download_fsr4(url: str, dst: str) -> None:
        urllib.request.urlretrieve(url, dst)

    if __setup_upscaler_files(
        prefix_dir,
        __fsr4_urls,
        __download_fsr4,
        __fsr4_version,
        os.path.join(compat_dir, __fsr4_version_file),
    ):
        log.info('Automatic FSR4 upgrade enabled')
    else:
        log.warn('Failed to download amdxcffx64.dll')


def setup_upscalers(compat_config: set, env: dict, compat_dir: str, prefix_dir: str) -> None:
    """Setup configured upscalers

    usage: setup_upscalers(g_session.compat_config, g_session.env, g_compatdata.base_dir, g_compatdata.prefix_dir)
    """
    loaddll_replace = set()
    if 'fsr4' in compat_config or 'fsr4rdna3' in compat_config:
        setup_fsr4(compat_dir, prefix_dir)
        if check_fsr4(compat_dir, prefix_dir):
            loaddll_replace.add('fsr4')
    if 'dlss' in compat_config:
        setup_dlss(compat_dir, prefix_dir)
        if check_dlss(compat_dir, prefix_dir):
            loaddll_replace.add('dlss')
    if "xess" in compat_config:
        setup_xess(compat_dir, prefix_dir)
        if check_xess(compat_dir, prefix_dir):
            loaddll_replace.add("xess")
    if "fsr3" in compat_config:
        setup_fsr3(compat_dir, prefix_dir)
        if check_fsr3(compat_dir, prefix_dir):
            loaddll_replace.add("fsr3")
    if loaddll_replace:
        env["WINE_LOADDLL_REPLACE"] = ",".join(loaddll_replace)


def setup_local_shader_cache(env: dict) -> None:
    """Setup per-game shader cache if shader pre-caching is disabled

    usage: setup_local_shader_cache(g_session.env)
    """
    path = os.environ.get("STEAM_COMPAT_SHADER_PATH", "")
    if not path:
        return
    shader_cache_name = "steamapp_shader_cache"
    shader_cache_vars = {
        # Nvidia
        "__GL_SHADER_DISK_CACHE_APP_NAME": shader_cache_name,
        "__GL_SHADER_DISK_CACHE_PATH": os.path.join(path, "nvidiav1"),
        "__GL_SHADER_DISK_CACHE_READ_ONLY_APP_NAME": "steam_shader_cache;steamapp_merged_shader_cache",
        "__GL_SHADER_DISK_CACHE_SIZE": "5000000000",
        "__GL_SHADER_DISK_CACHE_SKIP_CLEANUP": "1",
        # Mesa
        "MESA_DISK_CACHE_READ_ONLY_FOZ_DBS": "steam_cache,steam_precompiled",
        "MESA_DISK_CACHE_SINGLE_FILE": "1",
        "MESA_GLSL_CACHE_DIR": path,
        "MESA_GLSL_CACHE_MAX_SIZE": "5G",
        "MESA_SHADER_CACHE_DIR": path,
        "MESA_SHADER_CACHE_MAX_SIZE": "5G",
        # AMD VK
        "AMD_VK_PIPELINE_CACHE_FILENAME": shader_cache_name,
        "AMD_VK_PIPELINE_CACHE_PATH": os.path.join(path, "AMDv1"),
        "AMD_VK_USE_PIPELINE_CACHE": "1",
        # DXVK
        "DXVK_STATE_CACHE_PATH": os.path.join(path, "DXVK_state_cache"),
        # VKD3D
        "VKD3D_SHADER_CACHE_PATH": os.path.join(path, "VKD3D_shader_cache")
    }
    for (var, val) in shader_cache_vars.items():
        if var in os.environ:
            continue
        if var in {
            "__GL_SHADER_DISK_CACHE_PATH",
            "MESA_GLSL_CACHE_DIR",
            "MESA_SHADER_CACHE_DIR",
            "AMD_VK_PIPELINE_CACHE_PATH",
            "DXVK_STATE_CACHE_PATH",
            "VKD3D_SHADER_CACHE_PATH",
        }:
            os.makedirs(val, exist_ok=True)
        env[var] = val

