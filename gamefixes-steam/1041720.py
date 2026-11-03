"""Game fix for Kingdoms of Amalur: Re-Reckoning"""

from protonfixes import util


def main() -> None:
    """Textures flicker and parts of character models flicker in and out without the native shader compilers"""
    util.protontricks('d3dcompiler_43')
    util.protontricks('d3dcompiler_47')
