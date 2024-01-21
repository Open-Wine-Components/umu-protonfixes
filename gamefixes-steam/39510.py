""" Game fix for Gothic II: Gold Edition
"""
#pylint: disable=C0103

import glob
import os
from protonfixes import util


def main():

    screen_width,screen_height = util.get_resolution()

    zVidResFullscreenX=str(screen_width)
    zVidResFullscreenY=str(screen_height)

    """ Modify Gothic.ini
    """

    game_opts = """
    [GAME]
    scaleVideos=1
    [VIDEO]
    zVidResFullscreenX=""" + zVidResFullscreenX + """
    zVidResFullscreenY=""" + zVidResFullscreenY + """
    zVidResFullscreenBPP=32
    """

    # Localized versions use different casing for filenames
    ini_pattern = '[Ss][Yy][Ss][Tt][Ee][Mm]/[Gg][Oo][Tt][Hh][Ii][Cc].[Ii][Nn][Ii]'
    install_dir = glob.escape(util.get_game_install_path())
    ini_path = glob.glob(os.path.join(install_dir,ini_pattern))

    if len(ini_path) == 1:
        util.set_ini_options(game_opts,ini_path[0],'cp1251','absolute')

    # Fix the game getting locked on exit
    util.disable_fsync()
