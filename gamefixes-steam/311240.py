"""Game fix for Zero Escape: Zero Time Dilemma"""

from protonfixes import util

def main() -> None:
    """Disables libglesv2 to allow launcher to render """
    util.winedll_override('libglesv2', OverrideOrder.DISABLED)
