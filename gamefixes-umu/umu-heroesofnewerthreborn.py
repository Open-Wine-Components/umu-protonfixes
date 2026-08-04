"""Game fix for Heroes of Newerth Reborn"""

from protonfixes import util


def main() -> None:
    util.protontricks('gdiplus')
    util.protontricks('corefonts')
    util.protontricks('ie8')
    # Fixes effects rendering solid black. The game compiles shaders at
    # runtime and vkd3d-shader's HLSL compiler lacks reversebits.
    util.protontricks('d3dcompiler_47')
