"""Game fix for Smite 2
Will not launch without SteamDeck=0
"""

from protonfixes import util


def main() -> None:
    util.set_environment('SteamDeck', '0')
