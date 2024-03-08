""" Game fix for Final Fantasy VII
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ installs vcrun2019 and d3dcompiler47                
    """

    # FFVII needs vcrun2019 and d3dcompiler_47
    util.protontricks('vcrun2019')
    util.protontricks('d3dcompiler_47')
