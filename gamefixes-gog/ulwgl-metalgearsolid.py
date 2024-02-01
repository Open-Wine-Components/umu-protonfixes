""" 
METAL GEAR SOLID
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """
    override for wrapper shipped with the game
    """

    util.winedll_override('ddraw', 'n')
