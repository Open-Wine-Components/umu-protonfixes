"""Game fix for Limelight Lemonade Jam"""

from protonfixes import util


def main() -> None:
    util.winedll_override('version', util.OverrideOrder.NATIVE_BUILTIN)
    util.append_argument('-vomstyle=layer')
