"""Game fix for Dungeon Siege"""

from protonfixes import util


def main() -> None:
    """Enable Multiplayer and protontricks directplay for full functionality"""
    util.append_argument('Zonematch=true')
    util.protontricks('directplay')
