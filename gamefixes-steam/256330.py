""" WRC 4
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    #Black screen without it
    util.protontricks('d3dx9_42')
    util.protontricks('d3dx9_43')

    #Fixes background videos
    util.protontricks('wmp11')

    #Fixes audio sliders in options
    util.protontricks('xact')

    # Audio breaks above 60 fps, game engine issue
    util.set_environment('DXVK_FRAME_RATE', '60')
