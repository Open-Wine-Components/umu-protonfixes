"""Battle Engine Aquila"""

from protonfixes import util


def main() -> None:
    """Game needs dsound dlls to fix looping and overlapping sound in menus and ingame"""
    util.protontricks('dsound')
