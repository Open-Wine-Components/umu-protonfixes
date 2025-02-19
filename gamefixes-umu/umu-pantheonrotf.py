"""Game fix for Pantheon: Rise of the Fallen"""

from protonfixes import util


def main() -> None:
    # Standalone launcher fix
    util.protontricks('dotnet48')
    util.protontricks('win10')
