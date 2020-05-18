""" Game fix for Assetto Corsa
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ installs d3dcompiler, dotnet472
    """

    util.protontricks('d3dx11_43')
    util.protontricks('d3dcompiler_43')
    util.protontricks('dotnet472')
    util.protontricks('vcrun2008')
    util.protontricks('vcrun2010')
    util.protontricks('vcrun2012')
    util.protontricks('vcrun2013')
    util.protontricks('nocrashdialog')