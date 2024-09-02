"""Game fix for Forts"""

from protonfixes import util


def main() -> None:
    """Uses winetricks to install the ole32 verb"""
    util.protontricks('ole32')
