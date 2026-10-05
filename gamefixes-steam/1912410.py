"""Game fix for Minecraft Dungeons II

The title refuses to start without Microsoft Gaming Services. This installs a
local stand-in for xgameruntime.dll and signs the player in with their own
Microsoft account.

The stand-in is the MIT-licensed helper from
https://github.com/Kubas556/Dungeons2_linux_fix at
99eb7aec883808e835ef3799264730a3d81f23d7. Rebuild the DLL with
``x86_64-w64-mingw32-gcc-posix -shared -O2 -Wall -Wextra -o xgameruntime.dll xgameruntime.c``.
"""

import filecmp
import shutil
from pathlib import Path

from protonfixes import util
from protonfixes.logger import log

PAYLOAD = Path(__file__).resolve().parent / '_dungeons2'
COMPAT = Path.home() / '.local/share/dungeons2-compat'


def _dll_source() -> Path:
    checkout = COMPAT / 'src/xgameruntime.dll'
    if (COMPAT / '.git').is_dir() and checkout.is_file():
        return checkout
    return PAYLOAD / 'xgameruntime.dll'


def _install_helper() -> None:
    """Copy the sign-in script to the directory the DLL searches."""
    if (COMPAT / '.git').is_dir():
        log.info('Using the existing dungeons2-compat checkout')
        return
    if COMPAT.exists() and not COMPAT.is_dir():
        log.warn(f'{COMPAT} exists and is not a directory')
        return
    COMPAT.mkdir(parents=True, exist_ok=True)
    source = PAYLOAD / 'xauth.py'
    target = COMPAT / 'xauth.py'
    if target.is_file() and filecmp.cmp(source, target, shallow=False):
        return
    shutil.copy2(source, target)
    target.chmod(0o755)
    log.info(f'Installed {target}')


def _install_dll() -> None:
    dll = _dll_source()
    game = Path(util.get_game_install_path())
    targets = (
        game / 'xgameruntime.dll',
        game / 'Dungeons/Binaries/Win64/xgameruntime.dll',
        util.protonprefix() / 'drive_c/windows/system32/xgameruntime.dll',
    )
    for target in targets:
        if not target.parent.is_dir():
            log.warn(f'Missing {target.parent}; not installing xgameruntime.dll')
            continue
        if target.is_file() and filecmp.cmp(dll, target, shallow=False):
            continue
        shutil.copy2(dll, target)
        log.info(f'Installed {target}')


def main() -> None:
    """Install the Gaming Services stand-in and load it as a native DLL."""
    if shutil.which('openssl') is None:
        log.warn('openssl is not on PATH; Microsoft sign-in cannot run')
    _install_helper()
    _install_dll()
    util.winedll_override('xgameruntime', util.OverrideOrder.NATIVE)
