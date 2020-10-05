""" Game fix for Borderlands 3
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ This prevents a freeze after the 2k logo video
    """

    # Fixes the startup process.
    util.append_argument('-NoStartupMovies')

