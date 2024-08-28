"""Game fix for Full Metal Daemon Muramasa

This game is borked on gog due to audio synchronization (xaudio) issues. To
make this game playable, xaudio2_9.dll simply needs to be in the game
directory and renamed to xaudio2_8.dll.
"""

from protonfixes import util


def main():
    pass
