"""Fixes in-game media playback."""

from protonfixes import util


def main() -> None:
    util.protontricks('wmp9')
    util.protontricks('directshow')
