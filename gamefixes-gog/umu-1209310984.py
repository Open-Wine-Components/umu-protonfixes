"""Game fix for Full Metal Daemon Muramasa"""

from protonfixes import util


def main() -> None:
    util.disable_protonmediaconverter()
    util.winedll_override('wmvdecod', util.OverrideOrder.DISABLED)
