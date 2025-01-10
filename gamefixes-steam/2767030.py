"""Game fix for Marvel Rivals"""

from protonfixes import util


def main() -> None:
    """Game needs SteamDeck=1 to start since season 1"""
    util.set_environment('SteamDeck', '1')
