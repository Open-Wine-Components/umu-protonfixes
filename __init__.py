"""Starts the protonfix module and runs fixes after pre-flight-checks"""

import os
import sys
import traceback
from typing import Callable

from . import fix
from .logger import log
from .upscalers import setup_upscalers
from .utilities import (
    setup_frame_rate,
    setup_local_shader_cache,
    setup_mount_drives,
    winetricks,
)
from .zenity import ZenityWaitDialog

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
aarch64_lib_dir: str = (
    f'{os.path.dirname(os.path.realpath(__file__))}/files/lib/aarch64-linux-gnu'
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


def execute_early() -> None:
    """Execute the early part of protonfixes"""
    if check_iscriptevaluator():
        log.debug('Skipping fix execution. We are running "iscriptevaluator.exe".')
    elif not check_conditions():
        log.warn('Skipping fix execution. We are probably running a unit test.')
    else:
        fix.early()


execute_early()


def setup(
    env: dict,
    bin_path_var: str,
    lib_path_var: str,
    func: Callable[[dict, str, str, str], None],
) -> None:
    """Setup PATH and LD_LIBRARY_PATH to include protonfixes's binary and library paths"""
    func(env, bin_path_var, bin_dir, ':')
    func(env, lib_path_var, f'{x86_64_lib_dir}:{aarch64_lib_dir}:{i386_lib_dir}', ':')


def execute() -> None:
    """Execute protonfixes"""
    if check_iscriptevaluator():
        log.debug('Skipping fix execution. We are running "iscriptevaluator.exe".')
    elif not check_conditions():
        log.warn('Skipping fix execution. We are probably running a unit test.')
    else:
        dialog = ZenityWaitDialog('Installing Game-Specific fixes, please wait...')
        try:
            dialog.start()
            fix.main()

        except Exception:
            sys.stderr.write('ProtonFixes ' + traceback.format_exc())
            sys.stderr.flush()

        finally:
            dialog.stop()


__all__ = [
    'setup',
    'execute',
    'setup_frame_rate',
    'setup_local_shader_cache',
    'setup_mount_drives',
    'setup_upscalers',
    'winetricks',
]
