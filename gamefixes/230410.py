""" Game fix for Warframe
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Enable Async
    """

    # Enables dxvk async.
    util.enable_dxvk_async()
