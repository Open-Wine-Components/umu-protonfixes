""" FarCry 4
"""
#pylint: disable=C0103

from protonfixes import util


def main():
    """ FarCry 4 chokes on more than 24 cores
    """

    util.protontricks('d3dcompiler_43')
    util.protontricks('d3dcompiler_47')
