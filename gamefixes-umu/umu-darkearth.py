"""Game fix for Dark Earth (cd version)"""

from protonfixes import util


def main() -> None:
    """Apply protontricks cnc_ddraw to fix "Fatal Error : 8" when saving game"""
    util.protontricks('cnc_ddraw')
