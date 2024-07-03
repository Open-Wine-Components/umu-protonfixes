"""Game fix for Elden Ring: Manually create the `DLC.bdt` file to work around the "Inappropriate activity detected" error for players that don't own the DLC"""

from pathlib import Path
from protonfixes import util


def main():
    # Create the DLC.bdt file if it doesn't already exist, which is known to fix Easy AntiCheat not working for players that don't own the DLC
    # A blank file is enough to get multiplayer working
    Path(f"{util.get_game_install_path()}/Game/DLC.bdt").touch(exist_ok=True)
