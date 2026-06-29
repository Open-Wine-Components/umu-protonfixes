"""Call Winetricks GUI"""
import os

from protonfixes import util


def early() -> None:
    os.environ['PROTON_DLL_COPY'] = '*'


def main() -> None:
    """Requires seccomp"""
    util.protontricks('gui')
