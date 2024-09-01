"""Resident Evil (1997)"""

from protonfixes import util


def main() -> None:
    util.winedll_override('ddraw', 'n,b')
    util.winedll_override('dinput', 'n,b')
