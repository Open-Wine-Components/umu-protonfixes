""" Atelier Ryza: Ever Darkness & the Secret Hideout
Missing voices/sounds in cutscenes
Requires disabling the gstreamer protonaudioconverterbin plugin to get full audio in cutscenes
"""

#pylint: disable=C0103

from protonfixes import util

def main():
    util.disable_protonmediaconverter()
