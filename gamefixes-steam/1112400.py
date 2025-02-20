"""Game fix for Project Torque"""

from protonfixes import util


def main() -> None:
    """Game needs dotnet35 to launch"""
    """https://bugs.winehq.org/show_bug.cgi?id=57666"""
    util.protontricks('dotnet35sp1')
    util.protontricks('win10')
