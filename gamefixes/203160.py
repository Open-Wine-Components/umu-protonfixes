
""" Game fix for Tomb Raider 2013
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Improve smooth experience 
    """

    # reduce stuttering
    util.enable_dxvk_async()
