""" Game fix for Assetto Corsa
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """Fixes default launcher and ACM."""

    # Fixes Assetto itself and Content Manager. Version 4.5.2 does not seem to start.
    # Although CefSharp from Content Manager might have a higher requirement, it seems to
    # always crash on the GPU process so it doesn't really matter.
    util.protontricks('dotnet472')
    # Fixes Content Manager (black windows)
    util.protontricks('d3dx11_43')
    util.protontricks('d3dcompiler_47')
