"""Game fix for Just Cause 2"""

from protonfixes import util


def main() -> None:
    util.regedit_add('HKLM\\Software\\Wow6432Node\\GOG.com\\GalaxyClient')
    util.append_argument('-borderless')
