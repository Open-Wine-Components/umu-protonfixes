""" Game fix for FFXIV
"""
#pylint: disable=C0103

from protonfixes import util
import os

def main():
    """ for FFXIV hide wine exports to allow launcher to work.
    """

    # https://bugs.winehq.org/show_bug.cgi?id=47342
    util.protontricks('hidewineexports=enable')

    # launcher tries to render in d3d9, d9vk doesnt work with it yet
    util.disable_d3d9() 

    # disable new character intro cutscene to prevent black screen loop
    configpath = os.path.join(util.protonprefix(), 'drive_c/users/steamuser/My Documents/My Games/FINAL FANTASY XIV - A Realm Reborn')
    if not os.path.exists(configpath):
        os.makedirs(configpath)
    configgame = os.path.join(configpath, 'FFXIV.cfg')
    if not os.path.isfile(configgame):
        f = open(configgame,"w+")
        f.write("<FINAL FANTASY XIV Config File>\n\n<Cutscene Settings>\nCutsceneMovieOpening 1")
        f.close


