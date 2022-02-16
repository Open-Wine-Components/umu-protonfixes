""" Game fix for Heavy Rain
"""

#pylint: disable=C0103

from protonfixes import util
import os

# Heavy Rain has broken lip-syncing unless xaudio2_7 is forced to native.
def main():
    util.winedll_override('xaudio2_7', 'n')
