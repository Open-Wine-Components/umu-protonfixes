""" Alter Ego
Launcher crashes immediately without displaying any windows
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.replace_command('AlterEgo.exe', './RunDev.exe')
    util.append_argument('AlterEgo.ebr')
    util.set_environment('SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS', '0')
