""" 
Silent Hill 4: The Room
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.winedll_override('d3d8', 'n,b') # GOG's dxcfg / Steam006 fixes
    util.winedll_override('dinput8', 'n,b') # GOG's controller fix / Silent Hill 4: Wrapper by Nemesis / ThirteenAG's widescreen fix
    util.winedll_override('dsound', 'n,b') # Ultimate ASI Loader / Silent Hill 4 Randomizer
