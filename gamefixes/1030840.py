""" Mafia Definitive Edition
"""
#pylint: disable=C0103

from protonfixes import util
import os

def main():
    """ Requires seccomp
    """

    util.use_seccomp()
    util.replace_command('launcher.exe', 'mafiadefinitiveedition.exe')
    util.protontricks('d3dcompiler_47')
    configpath = os.path.join(util.protonprefix(), 'drive_c/users/steamuser/My Documents/My Games/Mafia Definitive Edition/Saves')
    if not os.path.exists(configpath):
        os.makedirs(configpath)
    configgame = os.path.join(configpath, 'videoconfig.cfg')
    if not os.path.isfile(configgame):
        f = open(configgame,"w+")
        f.write("-6 0 1920 1080 0 0 0 0 0")
        f.close
