"""Shadows on the Vatican - Act II: Wrath
Launcher keeps it's process running in the background but nothing shows up
"""

import os
from protonfixes import util


def main() -> None:
    util.replace_command('SotV_Launcher.exe', 'hd/SotV2.exe')
    os.chdir('hd')
