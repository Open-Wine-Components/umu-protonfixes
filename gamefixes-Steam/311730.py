""" Game fix for DEAD OR ALIVE 5 Last Round
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Disables esync
    """

    # https://github.com/ValveSoftware/Proton/issues/1834#issuecomment-433672443
    util.disable_esync()
    util.disable_fsync()
