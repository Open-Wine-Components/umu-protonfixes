""" Game fix for Star Trek Online launcher
"""
#pylint: disable=C0103
from protonfixes import util

def main():
    """ Ensure d3dcompiler_47 is installed so the launcher window content is visible
    """
    util.protontricks('d3dcompiler_47')
