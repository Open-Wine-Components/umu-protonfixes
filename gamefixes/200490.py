""" Memento Mori
wmp11 (Fixes missing logo videos and problems with working videos)
replace launch command (workaround for ProtonGE since 8.4)
hangs on logo without override
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.set_environment('WINEDLLOVERRIDES', 'libvkd3d-1=n')
    util.replace_command('run_game.cmd', 'memento.exe')
    util.append_argument('-lang:en,en')
    util.protontricks('wmp11')
