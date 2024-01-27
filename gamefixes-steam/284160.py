""" Game fix for BeamNG.drive
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ installs d3dx9_43, d3dcompiler_43, d3dx11_43, d3dcompiler_47
    """

    # https://github.com/ValveSoftware/Proton/issues/544#issuecomment-826150012
    util.protontricks('d3dx9_43')
    util.protontricks('d3dcompiler_43')
    util.protontricks('d3dx11_43')
    util.protontricks('d3dcompiler_47')
