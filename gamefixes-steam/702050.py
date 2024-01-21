""" Game fix for The Song of Saya
"""

from protonfixes import util

def main():
    """ Disable esync and fsync
    """

    # Fixes random crashing during gameplay
    util.disable_esync()
    util.disable_fsync()
