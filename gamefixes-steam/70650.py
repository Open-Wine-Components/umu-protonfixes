"""Game fix for Worms: Blast"""

from protonfixes import util


def main() -> None:
    """Installs directmusic to fix menu and game music"""
    util.protontricks('directmusic')
