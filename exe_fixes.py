"""Fixes for non-Steam (retail) games, matched by executable name

Retail games added to Steam as non-Steam shortcuts get a random app id, and
umu games without a database entry run as 'umu-0', so their fixes cannot be
keyed by game id. The default fix files call apply() to match them by the
name of the launched executable instead.
"""

import os
import sys

from .logger import log
from . import util


def _launched_exe() -> str:
    """Lower-case file name of the executable Proton was asked to run"""
    if len(sys.argv) < 3:
        return ''
    return os.path.basename(sys.argv[2].replace('\\', '/')).lower()


def _mem_total_mb() -> int:
    """Total host RAM in MiB, 0 if unknown"""
    try:
        with open('/proc/meminfo', encoding='ascii') as meminfo:
            for line in meminfo:
                if line.startswith('MemTotal:'):
                    return int(line.split()[1]) // 1024
    except (OSError, ValueError, IndexError):
        pass
    return 0


def vtmb_bloodlines_retail() -> None:
    """Vampire: The Masquerade - Bloodlines, retail release without patches

    engine.dll calls GlobalMemoryStatus() and compares dwTotalPhys with 15 MB
    as a signed 32-bit int. With more than 4 GB of RAM Wine reports 0xFFFFFFFF,
    which reads as -1, and the game exits with
    "Available memory less than 15MB!!! -1". The engine only uses half of that
    value, clamped to 80-200 MB, as its heap, so reporting 1.5 GB costs nothing.
    WINE_RAM_REPORTING_BIAS subtracts the given MiB from the reported RAM.

    The retail SafeDisc build is run through a version.dll loader placed next
    to vampire.exe, which has to be loaded instead of Wine's builtin.
    """
    if os.environ.get('SteamAppId') == '2600':  # Steam release, not the retail one
        return

    if 'WINE_RAM_REPORTING_BIAS' not in os.environ:
        total_mb = _mem_total_mb()
        target_mb = 1536
        if total_mb > target_mb:
            util.set_environment('WINE_RAM_REPORTING_BIAS', str(total_mb - target_mb))

    util.winedll_override('version', util.OverrideOrder.NATIVE_BUILTIN)


EXE_FIXES = {
    'vampire.exe': vtmb_bloodlines_retail,
}


def apply() -> None:
    """Run the fix for the launched executable, if there is one"""
    fix = EXE_FIXES.get(_launched_exe())
    if fix is None:
        return
    log.info(f'Using executable fix {fix.__name__} for {_launched_exe()}')
    fix()
