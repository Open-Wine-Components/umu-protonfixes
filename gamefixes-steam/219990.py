""" Game fix for Grim Dawn
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    # Fix black screen. Only needed in a Wine prefix that lacks the DirectX Redist installation that comes with the game installer.
    util.protontricks('d3dcompiler_43')
