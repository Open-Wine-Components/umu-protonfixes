""" The Blind Prophet
garbled fonts & No cursive font (Segoe Script)
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.winedll_override('d3d9', 'd')
    util.protontricks('segoe_script')
