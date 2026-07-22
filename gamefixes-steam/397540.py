"""Game fix for Borderlands 3"""

from protonfixes import util


def main() -> None:
    """Borderlands 3"""
    # Fixes the startup process.
    util.protontricks('d3dcompiler_47')
    # Fixes crash with BL SDK
    util.protontricks('vcrun2022')
