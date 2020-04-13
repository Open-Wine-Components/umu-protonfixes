""" Darksiders Warmastered Edition
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Needs native dxgi.
    """

    util.set_environment('WINEDLLOVERRIDES','dxgi=n')
