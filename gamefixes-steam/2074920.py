"""Game fix for The First Descendant"""

from protonfixes import util


def main() -> None:
    """Game Currently has some funkyness where it doesnt properly detect eac, works fine after game is started without connecting. Star Citizen used to need this too"""
    util.set_environment('WINE_BLOCK_HOSTS', 'modules-cdn.eac-prod.on.epicgames.com')
