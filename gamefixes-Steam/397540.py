""" Game fix for Borderlands 3
"""
#pylint: disable=C0103
from protonfixes import util


def main():
    """ Borderlands 3 vcrun2019 fix
    """
    # Fixes the startup process.
    util.protontricks('vcrun2019_ge')
    util.protontricks('d3dcompiler_47')
