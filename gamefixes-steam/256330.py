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
