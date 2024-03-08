""" 
The Wheel of Time
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.winedll_override('ddraw', 'n,b') # GOG's dxcfg
