"""Game fix for Elden Ring: Manually create the DLC.bdt file to work around the "Inappropriate activity detected" error for players that don't own the DLC"""

import pathlib
from util import get_game_install_path

def main():
	if not pathlib.Path(f"{get_game_install_path()}/DLC.bdt").exists():
		# Create the DLC.bdt file if it doesn't already exist, which is known to fix Easy AntiCheat not working for players that don't own the DLC
		# A blank file is enough to get multiplayer working
		open(f"{get_game_install_path()}/DLC.bdt", 'w').close()
