"""Geometry Dash"""

from protonfixes import util


def main() -> None:
    util.winedll_override('xinput1_4', 'n,b')  # Adds Geode Mod Support
