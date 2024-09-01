"""DOOM Eternal"""

from protonfixes import util


def main() -> None:
    util.append_argument('+com_skipSignInManager 1')
