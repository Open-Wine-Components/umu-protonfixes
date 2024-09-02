"""Game fix for Stronghold Crusader Extreme HD
Fixes Multiplayer
"""

from protonfixes import util


def main() -> None:
    """Installs directplay"""
    util.protontricks('directplay')
