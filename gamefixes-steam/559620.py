"""Game fix for Outlaws + A Handful of Missions"""

#
from protonfixes import util


def main() -> None:
    # Override ddraw (cutscenes+menu perf) and WinMM (Music)
    util.winedll_override('ddraw', util.OverrideOrder.NATIVE_BUILTIN)
    util.winedll_override('winmm', util.OverrideOrder.NATIVE_BUILTIN)
