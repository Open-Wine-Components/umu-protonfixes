"""Game fix for God of War: Ragnarok
Will not launch without SteamDeck=1
"""

from protonfixes import util

def main() -> None:
	util.set_environment('SteamDeck', '1')
