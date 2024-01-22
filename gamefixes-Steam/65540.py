""" Game fix for Gothic 1
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

    util.set_ini_options(game_opts,'Gothic.ini','cp1251','game')

    # Fix the game getting locked on exit
    util.disable_fsync()
