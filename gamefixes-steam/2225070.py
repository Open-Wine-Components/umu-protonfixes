"""Trackmania"""

from protonfixes import util


def main() -> None:
    util.winedll_override('dinput8', 'n,b')  # Adds openplanet plugin manager Support
