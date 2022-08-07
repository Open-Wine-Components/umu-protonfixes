""" Game fix for The King Of Fighters XIII (2013)

The game speed is tied to the frame rate and was designed to run at 60 fps (as most fighting games). But it has no internal frame cap, and runs extremelly fast for display devices with refresh rates higher than 60Hz) [source: https://www.pcgamingwiki.com/wiki/The_King_of_Fighters_XIII#Game_runs_too_fast]
"""
#pylint: disable=C0103
import os
from protonfixes import util


def main():
    try:
        current_cap = int(os.getenv("DXVK_FRAME_RATE", 0))
    except ValueError:
        current_cap = 0

    if not current_cap or current_cap > 60:
        util.set_environment("DXVK_FRAME_RATE", "60")

    # the fix below is not needed for the upstream Proton (for some reason is currently broken on GE builds). It skips the intro video [source: https://www.pcgamingwiki.com/wiki/The_King_of_Fighters_XIII#Game_crash_after_intro_logos]
    util.append_argument("-v")
