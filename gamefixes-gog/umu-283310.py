"""Game fix for Soulbringer"""

from protonfixes import util


def main() -> None:
    util.protontricks('mfc42')
    # util.protontricks('cnc_ddraw') cnc_ddraw breaks the gog version, it works fine with just mfc42
