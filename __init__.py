"""Starts the protonfix module and runs fixes after pre-flight-checks"""

import os
import subprocess
import sys
import traceback
from typing import Callable

from . import fix
from .logger import log

sys.path.insert(
    0,
    f'{os.path.dirname(os.path.realpath(__file__))}/_vendor',  # noqa: PTH120
)

bin_dir: str = f'{os.path.dirname(os.path.realpath(__file__))}/files/bin'
i386_lib_dir: str = (
    f'{os.path.dirname(os.path.realpath(__file__))}/files/lib/i386-linux-gnu'
)
x86_64_lib_dir: str = (
    f'{os.path.dirname(os.path.realpath(__file__))}/files/lib/x86_64-linux-gnu'
)


# This is needed for protonfixes
os.environ['PROTON_DLL_COPY'] = '*'


def check_conditions() -> bool:
    """Determine, if the actual game was executed and protonfixes isn't deactivated.

    Returns:
        bool: True, if the fix should be executed.

    """
    return (
        len(sys.argv) >= 1
        and 'STEAM_COMPAT_DATA_PATH' in os.environ
        and 'PROTONFIXES_DISABLE' not in os.environ
        and 'waitforexitandrun' in sys.argv[1]
    )


def check_iscriptevaluator() -> bool:
    """Determine, if we were invoked while running "iscriptevaluator.exe".

    Returns:
        bool: True, if we were invoked while running "iscriptevaluator.exe".

    """
    return len(sys.argv) >= 3 and 'iscriptevaluator.exe' in sys.argv[2]


def setup(
    env: dict,
    bin_path_var: str,
    lib_path_var: str,
    func: Callable[[dict, str, str, str], None],
) -> None:
    """Setup PATH and LD_LIBRARY_PATH to include protonfixes's binary and library paths"""
    func(env, bin_path_var, bin_dir, ':')
    func(env, lib_path_var, f'{x86_64_lib_dir}:{i386_lib_dir}', ':')


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
            if os.path.exists(directory) and not _is_directory_empty(directory):
                func('gamedrive', drive_map[directory], directory)


def execute() -> None:
    """Execute protonfixes"""
    if check_iscriptevaluator():
        log.debug('Skipping fix execution. We are running "iscriptevaluator.exe".')
    elif not check_conditions():
        log.warn('Skipping fix execution. We are probably running an unit test.')
    else:
        try:
            fix.main()

        # Catch any exceptions and print a traceback
        except Exception:
            sys.stderr.write('ProtonFixes ' + traceback.format_exc())
            sys.stderr.flush()


__all__ = ['setup', 'execute', 'winetricks', 'setup_mount_drives']
