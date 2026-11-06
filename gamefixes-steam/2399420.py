"""Game fix for Le Mans Ultimate"""

from protonfixes import util


def main() -> None:
    """Use the builtin d3dx11_43 and its CUR/ICO loader, the game crashes in VR without it"""
    util.winedll_override('d3dx11_43', util.OverrideOrder.BUILTIN)
