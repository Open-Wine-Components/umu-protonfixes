""" Game fix for FFX/X-2 HD Remaster
"""
#pylint: disable=C0103

from protonfixes import util
import os

def main():
    """
    """
    # disable new character intro cutscene to prevent black screen loop
    configpath = os.path.join(util.protonprefix(), 'drive_c/users/steamuser/My Documents/SQUARE ENIX/FINAL FANTASY X&X-2 HD Remaster')
    if not os.path.exists(configpath):
        os.makedirs(configpath)
    configgame = os.path.join(configpath, 'GameSetting.ini')
    if not os.path.isfile(configgame):
        f = open(configgame,"w+")
        f.write("Language=en")
        f.close
