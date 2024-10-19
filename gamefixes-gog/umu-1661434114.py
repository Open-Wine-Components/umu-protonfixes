"""Dino Crisis"""
# GOG-ID 1661434114

from protonfixes import util


def main() -> None:
    util.winedll_override('ddraw', util.OverrideOrder.NATIVE_BUILTIN)
    util.winedll_override('dinput', util.OverrideOrder.NATIVE_BUILTIN)
