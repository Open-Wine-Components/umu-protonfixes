"""Oddworld: Stranger's Wrath HD"""

from protonfixes import util


def main() -> None:
    util.protontricks('mfc90')  # The game crashes on launch without mfc90
