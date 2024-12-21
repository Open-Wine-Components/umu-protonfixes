"""Game fix for Zenless Zone Zero"""

from protonfixes import util


def main() -> None:
    """Needs gamedrive fix to detect proper install space"""
    util.set_game_drive(True)
