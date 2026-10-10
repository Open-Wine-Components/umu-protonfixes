"""Game fix for Way of the Samurai 4"""

from protonfixes import util


def main() -> None:
    """Use the native compiler for legacy D3D9 effects."""
    # Builtin fx_2_0 compilation lacks the sampler and state initializers used at startup.
    util.protontricks('d3dcompiler_47')
