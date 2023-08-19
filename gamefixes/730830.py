""" Escape From Monkey Island
replace launch command (workaround for ProtonGE since 8.4)
dgvoodoo2 to force anti-aliasing and higher resolution
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.replace_command('start.bat', 'monkey4.exe')
    util.replace_command('startConfig.bat', 'monkey.exe')
    util.protontricks('dgvoodoo2')
