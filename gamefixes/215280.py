""" Game fix for Secret World Legends
"""
#pylint: disable=C0103

from protonfixes import util
import os

import __main__ as protonmain

def main():
    util.protontricks('d3dx9_43')
    util.protontricks('d3dx11_43')
    util.protontricks('d3dcompiler_43')

