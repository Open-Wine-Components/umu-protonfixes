"""Atelier Ryza: Ever Darkness & the Secret Hideout
Missing voices/sounds in cutscenes
Requires disabling the gstreamer protonaudioconverterbin plugin to get full audio in cutscenes
"""

from protonfixes import util


def main() -> None:
    util.disable_protonmediaconverter()
