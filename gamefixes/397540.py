""" Game fix for Borderlands 3
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Enable preload options
    """
    # Enable preload options
    util.append_argument('-NoLauncher -notexturestreaming')

