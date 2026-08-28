"""Game fix for BIT.TRIP RUNNER"""

from protonfixes import util


def main() -> None:
    """Wine's builtin d3dx9_43 stubs ID3DXEffectCompiler::CompileShader.

    That produces "shader: failed to compile vertex shader". The game also
    exits if OpenAL32.dll is missing. Native D3DX9 / D3DCompiler from the
    June 2010 redistributable is required; installing the winetricks verbs
    without a native override is not enough because Proton still loads the
    builtin implementation.

    https://github.com/ValveSoftware/Proton/issues/915
    """
    util.protontricks('openal')
    util.protontricks('d3dcompiler_43')
    util.protontricks('d3dx9_43')
    util.winedll_override('d3dx9_43', util.OverrideOrder.NATIVE)
    util.winedll_override('d3dcompiler_43', util.OverrideOrder.NATIVE)
