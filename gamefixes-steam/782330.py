""" DOOM Eternal
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Requires seccomp
    """

    util.use_seccomp()
    util.append_argument('+com_skipSignInManager 1')
