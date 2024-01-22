""" Just Cause 2
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Requires seccomp
    """

    util.protontricks('d3dcompiler_43')
    util.protontricks('d3dcompiler_47')
    util.protontricks('d3dx10')
    util.append_argument('-borderless')

