"""Game fix for Darksiders"""

from protonfixes import util


def main() -> None:
    """Add d3dcompiler fixes"""
    util.protontricks('d3dcompiler_42')
    util.protontricks('d3dcompiler_43')
    util.protontricks('d3dcompiler_46')
    util.protontricks('d3dcompiler_47')
