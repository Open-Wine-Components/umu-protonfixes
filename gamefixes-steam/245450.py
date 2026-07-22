"""Game fix for Wizardry 8"""

from protonfixes import util


def main() -> None:
    """Needs mfc42 for settings dialog functionality"""
    util.protontricks('mfc42')
