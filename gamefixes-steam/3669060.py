"""Game fix for Blade & Soul NEO"""

from protonfixes import util


def main() -> None:
    util.protontricks('hidewineexports=enable')
    util.protontricks('dotnet48')
