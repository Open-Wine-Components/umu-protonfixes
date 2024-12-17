"""Game fix for Dungeon Siege"""

from protonfixes import util


def main() -> None:
    """Apply protontricks directplay for full multiplayer functionality"""
    util.protontricks('directplay')
