"""Game fix for Phantasy Star Online 2"""

from protonfixes import util


def main():
    util.set_environment('WINE_NO_OPEN_FILE_SEARCH', 'pso2_bin/data')
