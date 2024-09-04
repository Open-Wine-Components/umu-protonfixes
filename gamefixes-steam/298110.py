"""FarCry 4"""

from protonfixes import util


def main() -> None:
    """FarCry 4 chokes on more than 24 cores"""
    util.protontricks('d3dcompiler_43')
    util.protontricks('d3dcompiler_47')
