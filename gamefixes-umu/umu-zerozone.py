"""Game fix for Zero Zone"""

from protonfixes import util

def main() -> None:
    # Replace launcher with game exe in proton arguments
    util.protontricks('cnc_ddraw')
