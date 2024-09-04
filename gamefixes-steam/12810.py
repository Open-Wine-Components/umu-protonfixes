"""Overlord II"""

from protonfixes import util


def main() -> None:
    util.protontricks('physx')  # Game crashes without it
