""" Game fix for Fable III
"""

#pylint: disable=C0103

import os
import shutil

from protonfixes import util
from protonfixes.logger import log


def main():
    # https://www.reddit.com/r/SteamDeck/comments/vuagy2/finally_got_fable_3_working/
    util.protontricks('xliveless')

    # Remove Windows Live folder
    dirpath = os.path.join(util.protonprefix(),"drive_c","Program Files","Common Files","Microsoft Shared","Windows Live")
    if os.path.exists(dirpath):
        shutil.rmtree(dirpath)
    else:
        log(f"Path '{dirpath}' could not be found")
