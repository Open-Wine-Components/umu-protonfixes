"""Game fix for Bully: Scholarship Edition"""

from protonfixes import util


def main():
    """Video playback is working since GE-Proton 9.11 - without audio
    Disabling the media converter fixes this issue
    """
    util.disable_protonmediaconverter()
