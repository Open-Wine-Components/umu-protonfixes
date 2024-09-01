"""Game fix for WORLD OF HORROR"""

from protonfixes import util


def main():
    """Disable esync"""

    # esync causes occasional crashing
    util.disable_esync()
