"Game fix for God of War: Ragnarok"
from os import environ

def main():
	# Game won't launch on non-Steam Deck systems without this environment variable
	environ['SteamDeck'] = '1'
