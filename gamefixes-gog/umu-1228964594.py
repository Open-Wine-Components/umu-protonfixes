""" Game fix for Soldier of Fortune II: Double Helix - Gold Edition 
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    # Fix display issues
    util.set_environment('MESA_EXTENSION_MAX_YEAR', '2003')
    util.set_environment('__GL_ExtensionStringVersion', '17700')
