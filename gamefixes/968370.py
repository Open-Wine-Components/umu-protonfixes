""" The Blind Prophet
garbled fonts & No cursive font (Segoe Script)
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.set_environment('WINEDLLOVERRIDES', 'd3d9=d')
    util.protontricks('segoe_script')
