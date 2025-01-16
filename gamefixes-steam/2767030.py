"""Game fix for Marvel Rivals"""

from protonfixes import util


def main() -> None:
    """Game needs SteamDeck=1 not to crash on start-up"""
    util.set_environment('SteamDeck', '1')
