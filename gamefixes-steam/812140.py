"""Assassin's Creed: Odyssey"""

from protonfixes import util


def main():
    """disable Easy Anti-Cheat and online play, disable uplay overlay and change closebehavior"""
    util.disable_uplay_overlay()

    # Replace launcher with game exe in proton arguments
    util.append_argument("-eac_launcher -nosplash")
