""" Game fix for Path of Exile
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Enable preload options
    """
    # Enable preload options
    util.set_environment('WINEDLLOVERRIDES','dxgi=n')

