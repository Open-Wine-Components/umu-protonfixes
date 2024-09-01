"""Call Winetricks GUI"""

from protonfixes import util


def main():
    """Requires seccomp"""

    util.protontricks('gui')
