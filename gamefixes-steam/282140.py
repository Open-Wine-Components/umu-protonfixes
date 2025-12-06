"""Game fix for SOMA"""

import os
from protonfixes import util


def main() -> None:
    util.disable_ntsync()
