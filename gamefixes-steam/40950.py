"""Game fix for Stronghold HD
Fixes Multiplayer
"""

from protonfixes import util


def main() -> None:
    """Installs directplay"""
    util.protontricks('directplay')
