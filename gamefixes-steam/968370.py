"""The Blind Prophet
garbled fonts & No cursive font (Segoe Script)
"""

from protonfixes import util


def main() -> None:
    util.winedll_override('d3d9', util.OverrideOrder.DISABLED)
    util.protontricks('segoe_script')
