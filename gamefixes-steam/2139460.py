"""Game fix for Once Human"""

from protonfixes import util


def main() -> None:
    """Advertises drive space to fixing caching"""
    util.set_environment('PROTON_SET_GAME_DRIVE', '1')
