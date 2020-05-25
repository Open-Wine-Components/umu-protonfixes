""" Game fix for Assetto Corsa
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ installs d3dcompiler, dotnet40
    """

    util.protontricks('d3dx11_43')
    util.protontricks('d3dcompiler_43')
    util.protontricks('dotnet472')
