"""Game fix for JR East Train Simulator"""

from protonfixes import util


def main() -> None:
    """Add misc. fixes"""
    util.protontricks('d3dcompiler_43')
    util.protontricks('vcrun2008')
