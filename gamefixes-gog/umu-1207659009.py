"""Fix for The Journeyman Project 3: Legacy of Time"""

from protonfixes import util


def main() -> None:
    util.create_dos_device('d', path=f'{util.get_game_install_path()}/data')
