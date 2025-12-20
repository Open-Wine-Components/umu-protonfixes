"""Game fix for Plants vs. Zombies: Game of the Year

Fixes slowdown when Crazy Dave is on screen or when selecting plant loadout at start of level.
The fix replaces the incorrect game executable with the correct one from the prefix, which only appears after the main executable runs.

YT Tutorial for slowdown fix: https://www.youtube.com/watch?v=EK1HyVGlHvY
Source of previous changedir fix: https://github.com/JamesHealdUK/protonfixes/blob/master/fixes/3590.sh
"""

import os
import shutil
import signal
import time
import threading
from pathlib import Path
from protonfixes import util
from protonfixes.logger import log


def _fix_executable() -> None:
    """Wait for correct exe in prefix, then copy it as PlantsVsZombies_good.exe"""
    prefix = util.protonprefix()
    src = prefix / 'drive_c/ProgramData/PopCap Games/PlantsVsZombies/popcapgame1.exe'
    game_dir = Path(util.get_game_install_path())
    good_exe = game_dir / 'PlantsVsZombies_good.exe'

    if good_exe.exists():
        return

    # Poll for up to 60 seconds
    for _ in range(120):
        if src.exists():
            time.sleep(0.5)
            try:
                shutil.copy2(src, good_exe)
                log.info('PvZ executable fix applied - restarting game')
                # Kill the current game process so Steam restarts it with correct exe
                os.kill(os.getpid(), signal.SIGTERM)
            except Exception as e:
                log.warn(f'Failed to apply PvZ fix: {e}')
            return
        time.sleep(0.5)


def main() -> None:
    """Changes the proton argument from the launcher to the game"""
    # Game expects this to be set
    util.append_argument('-changedir')

    game_dir = Path(util.get_game_install_path())
    if game_dir.joinpath('PlantsVsZombies_good.exe').exists():
        util.replace_command('PlantsVsZombies.exe', 'PlantsVsZombies_good.exe')
    else:
        threading.Thread(target=_fix_executable, daemon=True).start()
