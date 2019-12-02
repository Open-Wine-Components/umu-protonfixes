""" Game fix for Path of Exile
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Enable Async and add preload options
    """

    util.append_argument('--waitforpreload --nologo --gc2')

    # Enables dxvk async.
    util.enable_dxvk_async()

