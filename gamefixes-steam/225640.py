"""Game fix for Sacred 2 Gold"""

from protonfixes import util


def main() -> None:
    """Install physx"""
    util.protontricks('physx')
