""" Game fix Mass Effect Legendary Edition
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ 
    """
    util.protontricks('d3dcompiler_47')
    util.set_environment('WINEDLLOVERRIDES','openal32=b')


