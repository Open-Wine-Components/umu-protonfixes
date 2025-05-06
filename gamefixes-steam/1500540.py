"""Hardwar"""

from protonfixes import util


def main() -> None:
    util.winedll_override(
        'dinput', util.OverrideOrder.NATIVE_BUILTIN
    )  # DxWrapper component
    util.winedll_override('winmm', util.OverrideOrder.NATIVE_BUILTIN)  # Music playback
