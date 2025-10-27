"""Game fix for Richard Burns Rally"""

#
from protonfixes import util


def main() -> None:
    # Override ddraw (cutscenes+menu perf) and WinMM (Music)
    util.winedll_override('mfc70', util.OverrideOrder.NATIVE_BUILTIN)
    util.winedll_override('mfc71', util.OverrideOrder.NATIVE_BUILTIN)
    util.winedll_override('msvci70', util.OverrideOrder.NATIVE_BUILTIN)
    util.winedll_override('msvcp70', util.OverrideOrder.NATIVE_BUILTIN)
    util.winedll_override('msvcp71', util.OverrideOrder.NATIVE_BUILTIN)
    util.winedll_override('msvcr71', util.OverrideOrder.NATIVE_BUILTIN)
