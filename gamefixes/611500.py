""" Game fix for Quake Champions
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Emable DXVK async and disable esync.
    """

    util.enable_dxvk_async()
    util.disable_esync()
