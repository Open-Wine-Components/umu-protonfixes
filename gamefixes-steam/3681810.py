"""Game fix for Blue Protocol: Star Resonance"""

from protonfixes import util


def main() -> None:
    """Setting prefix to Windows 7 is needed for videos to play correctly"""
    util.protontricks('win7')
