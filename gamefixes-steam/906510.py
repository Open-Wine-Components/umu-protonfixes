
""" Game fix for Conception PLUS: Maidens of the Twelve Stars
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ installs d3dcompiler_47
    """

    # https://github.com/ValveSoftware/Proton/issues/3493#issuecomment-1521636321
    util.protontricks('d3dcompiler_47')
