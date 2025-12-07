"""Game fix for SOMA"""

from protonfixes import util


def main() -> None:
    util.disable_ntsync()
