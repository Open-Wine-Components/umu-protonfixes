"""Game fix for Once Human"""

from protonfixes import util


def main() -> None:
    """Advertises drive space to fixing caching"""
    util.set_game_drive(True)
