""" Game fix for Age Of Empire 3: Complete Collection
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ installs d3dcompiler, dotnet472
    """

    util.protontricks('d3dx11_43')
    util.protontricks('d3dcompiler_43')
    util.protontricks('dotnet472')