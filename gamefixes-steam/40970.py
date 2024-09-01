"""Game fix for Stronghold Crusader HD
Fixes Multiplayer
"""

from protonfixes import util


def main():
    """Installs directplay"""

    util.protontricks('directplay')
