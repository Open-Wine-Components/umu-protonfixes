""" WRC 4
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    #Black screen without it
    util.protontricks('d3dx9_42')
    util.protontricks('d3dx9_43')
    util.protontricks('faudio')
    util.protontricks('xact')

    # Audio breaks above 60 fps
    util.set_environment('DXVK_FRAME_RATE', '60')
