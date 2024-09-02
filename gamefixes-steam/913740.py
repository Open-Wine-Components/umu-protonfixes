"""Game fix for WORLD OF HORROR"""

from protonfixes import util


def main() -> None:
    """Disable esync"""
    # esync causes occasional crashing
    util.disable_esync()
