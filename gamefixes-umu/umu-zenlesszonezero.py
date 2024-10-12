"""Game fix for Zenless Zone Zero"""

from protonfixes import util


def main() -> None:
    """Needs gamedrive fix to detect proper install space"""
    util.set_environment('PROTON_SET_GAME_DRIVE', 'gamedrive')

