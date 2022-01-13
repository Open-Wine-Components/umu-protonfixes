
""" Game fix for Lord of the Rings: War in the North
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Changes the proton argument from the launcher to the game
    """

    # reduce stuttering
    util.enable_dxvk_async()
