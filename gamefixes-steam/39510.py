""" Game fix for Gothic II: Gold Edition
"""
#pylint: disable=C0103

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
    install_dir = util.get_game_install_path()
    ini_path = os.path.join(install_dir,'System/Gothic.ini')

    util.set_ini_options(game_opts,ini_path,'cp1251','absolute')

    # Fix the game getting locked on exit
    util.disable_fsync()
    # GOG specific, Steam build doesn't have ddraw
    util.winedll_override("ddraw", "n,b")
