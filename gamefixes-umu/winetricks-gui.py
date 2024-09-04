"""Call Winetricks GUI"""

from protonfixes import util


def main() -> None:
    """Requires seccomp"""
    util.protontricks('gui')
