""" Game fix for Watch_Dogs
"""

#pylint: disable=C0103

from protonfixes import util
import os

# Watch_Dogs crashes if we don't force xaudio2_7 to native.
# Forcing watch_dogs.exe to run as Windows XP x64 allows for sound effects to work correctly.
def main():
    util.regedit_add("HKCU\\Software\\Wine\\AppDefaults\\watch_dogs.exe",'Version','REG_SZ','winxp64')
    util.winedll_override('xaudio2_7', 'n')
