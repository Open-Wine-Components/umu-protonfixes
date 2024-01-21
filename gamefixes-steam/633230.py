""" Game fix for Naruto To Boruto
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.replace_command('NARUTO.exe', 'NARUTO/Binaries/Win64/NARUTO-Win64-Shipping.exe')
    util.append_argument('-eac-nop-loaded')

    util.protontricks('hidewineexports=enable')

