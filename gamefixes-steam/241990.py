"""Game fix for Sorcerer King"""

from protonfixes import util


def main() -> None:
    util.protontricks('usp10')
    util.protontricks('vcrun2008')
    util.protontricks('vcrun2015')
    util.protontricks('d3dx9')
    util.protontricks('d3dcompiler_43')
    util.protontricks('d3dcompiler_47')
    util.winedll_override('SDNXLFonts', util.OverrideOrder.DISABLED)
