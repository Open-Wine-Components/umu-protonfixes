"""Game fix for Horizon Zero Dawn"""

from protonfixes import util


def main() -> None:
    # C++ runtime is not provided in the manifest
    util.protontricks('vcrun2019')
