"""Final Fantasy VII Rebirth"""

from protonfixes import util


def main() -> None:
    """Grants bonus items to players with save data for Final Fantasy VII Remake Intergrade"""
    util.import_saves_folder(1462040, 'Documents/My Games/FINAL FANTASY VII REMAKE')
