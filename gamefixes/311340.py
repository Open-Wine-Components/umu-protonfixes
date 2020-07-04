""" MGS: Ground Zeroes
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ needs native dxgi
    """

    util.set_environment('WINEDLLOVERRIDES','dxgi=n')
