""" Deliver us the Moon fix
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ 
    """

    # Replace launcher with game exe in proton arguments
    util.replace_command('MoonMan.exe', 'MoonMan/Binaries/Win64/MoonMan-Win64-Shipping.exe')

