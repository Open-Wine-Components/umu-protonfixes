"""Game fix for State of Decay 2"""

from protonfixes import util


def main() -> None:
    """Fix game crashes with d3dcompiler_47 and multiplayer crashes with win7"""
    util.protontricks('d3dcompiler_47')
    util.protontricks('win7')
