"""Game fix for MONGIL: STAR DIVE"""

from protonfixes import util

def early() -> None:
    """Needs gamedrive fix to detect proper install space"""
    util.set_game_drive(True)

def main() -> None:
    """Needs vcrun2022 to boot the game"""
    util.protontricks('vcrun2022')
