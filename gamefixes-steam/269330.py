"""Game fix for Chronology"""

from protonfixes import util


def main() -> None:
    """Add dotnet"""
    util.protontricks('dotnet20')
    util.protontricks('dotnet40')
