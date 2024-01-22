""" Game fix for Endless Legend
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Enable -useembedded to get past loading hang
    """
    # Enable preload options
    util.append_argument('-useembedded')

