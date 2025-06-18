"""Anno 1800"""

from protonfixes import util


def main() -> None:
    """Game ships with outdated uPlay launcher, which will not install to be able to start the game"""
    util.protontricks('ubisoftconnect')
