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


# DLSS and XeSS links taken from https://github.com/beeradmoore/dlss-swapper-manifest-builder/blob/main/manifest.json
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
