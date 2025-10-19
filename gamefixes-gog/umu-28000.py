"""Game fix for Kane & Lynch 2: Dog Days"""

from protonfixes import util


def main() -> None:
    util.regedit_add('HKLM\\Software\\Wow6432Node\\GOG.com\\GalaxyClient')
