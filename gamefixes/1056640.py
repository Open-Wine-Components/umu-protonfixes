""" Game fix for Phantasy Star Online 2
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ 
    """

    util.set_environment('WINE_NO_OPEN_FILE_SEARCH','pso2_bin/data')

