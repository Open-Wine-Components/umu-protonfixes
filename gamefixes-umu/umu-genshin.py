"""Game fix for Genshin Impact"""

from protonfixes import util


def main() -> None:
    """By default umu runs games on start.exe outside steam.
    However, Genshin's AC needs the game to be run from steam.exe to run on Linux.
    """
    util.set_environment('UMU_USE_STEAM', '1')
