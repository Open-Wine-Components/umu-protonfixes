"""MONSTER HUNTER RISE"""

from protonfixes import util


def main() -> None:
    util.winedll_override('dinput8', 'n,b')  # Enables REFramework to hook the game and enable Mods
