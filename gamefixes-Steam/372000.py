""" Game fix Tree Of Savior
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ https://forum.treeofsavior.com/t/linux-the-graphic-card-does-not-support-directx11-13ep/418073/13
    """
    util.protontricks('d3dcompiler_47')
