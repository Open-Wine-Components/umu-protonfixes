""" Resident Evil 4
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Requires seccomp
    """

    util.protontricks('d3dcompiler_43')
    util.protontricks('xactengine3_7_ge')
