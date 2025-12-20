"""Various utility functions for use in the proton script"""

import os
import subprocess
import sys
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


def setup_frame_rate(env: dict, func: Callable[[dict, str, str, str], None]) -> None:
    """Emulate DXVK/VKD3D_FRAME_RATE options using DXVK_CONFIG

    usage: setup_frame_rate(g_session,env. prepend_to_env_str)
    """
    frame_rate = env.pop(
        'DXVK_FRAME_RATE',
        env.pop('VKD3D_FRAME_RATE', env.pop('PROTON_FRAME_RATE', None)),
    )
    if frame_rate is not None:
        func(env, 'DXVK_CONFIG', f'dxgi.maxFrameRate={frame_rate}', ';')
        func(env, 'DXVK_CONFIG', f'd3d9.maxFrameRate={frame_rate}', ';')


def setup_local_shader_cache(compat_config: set, env: dict) -> None:
    """Setup per-game shader cache if shader pre-caching is disabled

    usage: setup_local_shader_cache(g_session.env)
    """
    if 'localshadercache' not in compat_config:
        return
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
        #'__GL_SHADER_DISK_CACHE_SKIP_CLEANUP': '1',
        # Mesa
        'MESA_DISK_CACHE_READ_ONLY_FOZ_DBS': 'steam_cache,steam_precompiled',
        'MESA_DISK_CACHE_SINGLE_FILE': '1',
        'MESA_GLSL_CACHE_DIR': path,
        'MESA_GLSL_CACHE_MAX_SIZE': '10G',
        'MESA_SHADER_CACHE_DIR': path,
        'MESA_SHADER_CACHE_MAX_SIZE': '10G',
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
        if var in {
            '__GL_SHADER_DISK_CACHE_PATH',
            'MESA_GLSL_CACHE_DIR',
            'MESA_SHADER_CACHE_DIR',
            'AMD_VK_PIPELINE_CACHE_PATH',
            'DXVK_STATE_CACHE_PATH',
            'VKD3D_SHADER_CACHE_PATH',
        }:
            os.makedirs(val, exist_ok=True)
        env.setdefault(var, val)
