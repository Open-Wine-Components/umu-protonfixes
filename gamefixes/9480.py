""" Saints Row 2
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    # Saints Row 2 default WMA audio doesn't work with faudio+gstreamer, need to fall back to standard faudio
    util.protontricks('faudio')
 
