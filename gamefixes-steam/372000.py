"""Game fix Tree Of Savior"""

from protonfixes import util


def main() -> None:
    """https://forum.treeofsavior.com/t/linux-the-graphic-card-does-not-support-directx11-13ep/418073/13"""
    util.protontricks('d3dcompiler_47')
    # Installing Quartz allows the game to work on GE 10-1
    util.protontricks('quartz')
