"""Game fix for Zero Escape: Zero Time Dilemma"""

from protonfixes import util

def main() -> None:
    util.winedll_override('libglesv2', util.OverrideOrder.DISABLED)

