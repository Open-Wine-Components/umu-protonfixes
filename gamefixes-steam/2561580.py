"""Horizon Zero Dawn Remastered"""

from protonfixes import util


def main() -> None:
    """Game allows playing saves from the original Complete Edition, but by default it can't find them."""
    util.import_saves_folder(1151640, 'My Documents/Horizon Zero Dawn')
