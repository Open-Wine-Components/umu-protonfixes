""" Game fix for FFXIV
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ for FFXIV hide wine exports to allow launcher to work.
    """

    # https://bugs.winehq.org/show_bug.cgi?id=47342
    util.protontricks('hidewineexports=enable')
