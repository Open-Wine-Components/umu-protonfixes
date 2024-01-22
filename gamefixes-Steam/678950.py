""" Game fix for DRAGON BALL FighterZ
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.replace_command('DBFighterZ.exe', 'RED/Binaries/Win64/RED-Win64-Shipping.exe')
    util.append_argument('-eac-nop-loaded')

    util.protontricks('hidewineexports=enable')
