""" Incoming Trilogy
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.winedll_override('d3d8', 'n,b')
    util.winedll_override('ddraw', 'b')
    util.winedll_override('winmm', 'n,b')
