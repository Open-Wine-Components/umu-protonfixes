""" Game fix for Secret World Legends
"""
#pylint: disable=C0103

from protonfixes import util
import os

def main():
    util.protontricks('d3dx9_43')
    util.protontricks('d3dx11_43')
    util.protontricks('d3dcompiler_43')

    # Breaks with dxvk's d3d9 implementation. Works with builtin. The game
    # itself runs well in d3d11 mode with dxvk, so we just do this one override
    # instead of falling completely back to wined3d.

    overrides = os.environ.get('WINEDLLOVERRIDES', "")
    if overrides != "":
        overrides += ','

    overrides += 'd3d9=b'

    util.set_environment('WINEDLLOVERRIDES',overrides)
