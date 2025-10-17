"""Game fix for Mafia: Definitive Edition"""

from protonfixes import util


def main() -> None:
    util.regedit_add('HKLM\\Software\\Wow6432Node\\GOG.com\\GalaxyClient')
