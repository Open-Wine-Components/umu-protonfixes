"""
METAL GEAR SOLID
"""

from protonfixes import util


def main():
    """
    override for wrapper shipped with the game
    """

    util.winedll_override('ddraw', 'n,b')
    util.winedll_override('dinput', 'n,b')
