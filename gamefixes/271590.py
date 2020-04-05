""" Game fix for Grand Theft Auto V
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Needs winedbg.exe disabled for multi-player.
    """

    util.set_environment('WINEDLLOVERRIDES','winedbg.exe=d')
