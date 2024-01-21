""" Game fix for Halo 3 mod tools
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    # Requires vcrun2019 to launch
    util.protontricks('vcrun2019_ge')
    util.protontricks('d3dcompiler_47')
    util.protontricks('msxml3')
