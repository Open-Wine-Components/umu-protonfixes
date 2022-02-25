""" Game fix for Elden Ring
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ EAC disable workaround
    """

    # Fixes the startup process.
    util.replace_command('start_protected_game.exe', 'eldenring.exe')
