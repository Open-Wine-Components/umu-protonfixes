"""Cardfight!! Vanguard Dear Days 2"""

from protonfixes import util


def main() -> None:
    """Imports player cards from  Cardfight!! Vanguard Dear Days. Yes that save path is indeed VG2 no idea why"""
    util.import_saves_folder(1881420, 'Saved Games/VG2/SAVELOAD')
