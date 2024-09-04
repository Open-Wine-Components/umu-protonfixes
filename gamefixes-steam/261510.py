"""Game fix for Tesla Effect"""

from protonfixes import util


def main() -> None:
    """Install corefonts"""
    # https://github.com/ValveSoftware/Proton/issues/1317
    util.protontricks('corefonts')
