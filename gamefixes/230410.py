""" Game fix Warframe
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Disable libglesv2 """

    # gpu acelleration on wibed3d https://bugs.winehq.org/show_bug.cgi?id=44985
    util.winedll_override('libglesv2', 'd')
