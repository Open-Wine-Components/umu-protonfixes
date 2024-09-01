"""Game fix for Stronghold Crusader Extreme HD
Fixes Multiplayer
"""

from protonfixes import util


def main():
    """Installs directplay"""

    util.protontricks('directplay')
