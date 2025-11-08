"""Game fix for Duet Night Abyss"""

from protonfixes import util


def main() -> None:
    """Installing dotnet48 fixes CEF issues (e.g. in-game news not loading)"""
    util.protontricks('dotnet48')
