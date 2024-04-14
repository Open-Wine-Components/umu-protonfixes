""" Atelier Ryza 2: Lost Legends & the Secret Fairy
Missing voices/sounds in cutscenes
Requires disabling the gstreamer protonaudioconverterbin plugin to get full audio in cutscenes
"""

#pylint: disable=C0103

from protonfixes import util

def main():
    util.disable_protonmediaconverter()
