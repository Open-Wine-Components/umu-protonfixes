""" Mortal Kombat 11
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Requires media foundation dlls and mem_alloc mod
    """

    util.wine_mem_alloc_mod()
    util.protontricks('mf_install')
 
