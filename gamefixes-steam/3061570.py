"""Game fix for Persona5: The Phantom X"""

from protonfixes import util

def early() ->  None:
    """Needs gamedrive fix to detect proper install space"""
    util.set_environment('PROTON_SET_GAME_DRIVE', '1')
