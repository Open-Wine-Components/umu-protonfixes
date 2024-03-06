""" Game fix for Grim Dawn
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    # Fix black screen. Needed for the expansions, not for the base game:
    util.protontricks('d3dcompiler_43')
