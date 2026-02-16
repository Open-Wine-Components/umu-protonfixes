"""Game fix for Zenless Zone Zero"""

from protonfixes import util


def early() -> None:
    """Needs gamedrive fix to detect proper install space"""
    util.set_game_drive(True)


def main() -> None:
    """By default umu runs games on start.exe outside steam.
    However, Zenless's AC needs the game to be run from steam.exe to run on Linux.
    """
    util.set_environment('UMU_USE_STEAM', '1')
    util.set_environment('WINE_DISABLE_VULKAN_OPWR', '1')
