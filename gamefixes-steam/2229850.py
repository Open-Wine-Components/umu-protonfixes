""" Game fix for Command & Conquer Red Alert™ 2 and Yuri’s Revenge™
"""
#pylint: disable=C0103

import os

from protonfixes import util
from protonfixes.logger import log

def main():
    """ Launch CnCNet Launcher - if installed, install it if requested

        The game crashes, when the launcher and it's patches are installed
        and Ra2.exe or RA2MD.exe are called directly by Steam.
        For this reason we must always use the launcher, if present.

        The game will just show a black screen without cnc-ddraw or the patch in place.
    """

    # User requested to install the CnCnet Launcher
    if os.environ.get('INSTALL_CNCNET'):
        log('User wants to install CnCnet Launcher')
        util.protontricks('cncnet_ra2')

    # CnCnet Launcher is in place, run it
    if os.path.isfile('CnCNetYRLauncher.exe'):
        log('CnCnet Launcher found, bypass game execution!')
        util.replace_command('Ra2.exe', 'CnCNetYRLauncher.exe')
        util.replace_command('RA2MD.exe', 'CnCNetYRLauncher.exe')
    else:
        # Return early, if cnc_ddraw is installed or failed to install
        if not util.protontricks('cnc_ddraw'):
            log('cnc-ddraw found!')
            return

        # After installing cnc_ddraw, we need to prevent the game
        # from loading the local ddraw.dll, instead of our override.
        # Note: This is only done once.
        if os.path.isfile('ddraw.dll'):
            log('Renaming local ddraw.dll to ddraw.dll.bak')
            os.rename('ddraw.dll', 'ddraw.dll.bak')
