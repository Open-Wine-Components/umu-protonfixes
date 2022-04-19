""" Game fix for Final Fantasy VII
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ installs vcrun2019_ge and d3dcompiler47                
    """

    # FFVII needs vcrun2019 and d3dcompiler_47
    util.protontricks('vcrun2019_ge')
    util.protontricks('d3dcompiler_47')

