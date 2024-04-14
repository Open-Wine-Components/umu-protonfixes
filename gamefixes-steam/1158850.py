""" The Great Ace Attorney Chronicles
Missing sound in bonus content videos
Requires disabling the gstreamer protonaudioconverterbin to get full audio
"""

# pylint: disable=C0103

from protonfixes import util


def main():
    util.disable_protonmediaconverter()
