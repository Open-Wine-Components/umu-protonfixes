"""Lethal Company"""

from protonfixes import util


def main() -> None:
    util.winedll_override('winhttp', 'n,b')  # Adds BepInEx Support
