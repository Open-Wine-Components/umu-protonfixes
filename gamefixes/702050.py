""" Game fix for The Song of Saya
"""

from protonfixes import util

def main():
    """ Disables ESYNC and FSYNC
    """

    # Fixes random crashing during gameplay
    util.set_environment('PROTON_NO_ESYNC', '1')
    util.set_environment('PROTON_NO_FSYNC', '1')
