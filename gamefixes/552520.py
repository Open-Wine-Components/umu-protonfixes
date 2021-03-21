""" Game fix for FarCry 5
"""
#pylint: disable=C0103

import os
from protonfixes import util

def main():
    """ disable Easy Anti-Cheat and online play, disable uplay overlay and change closebehavior
    """

    uplayconfigpath = os.path.join(util.protonprefix(), 'drive_c/users/steamuser/Local Settings/Application Data/Ubisoft Game Launcher')
    if not os.path.exists(uplayconfigpath):
        os.makedirs(uplayconfigpath)
    uplayconfigfile = os.path.join(uplayconfigpath, 'settings.yml')
    if not os.path.isfile(uplayconfigfile):
        f = open(uplayconfigfile,"w+")
        f.write("overlay:\n  enabled: false\n  fps_enabled: false\n  warning_enabled: false\nuser:\n  closebehavior: CloseBehavior_Close\n  landingpage: LandingPageLastPlayedGame\n")
        f.close

