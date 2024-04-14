""" Game fix for NUKITASHI
"""

from protonfixes import util

def main():
    """ Disable protonaudioconverterbin plugin
    """

    # Fixes audio not playing for in-game videos
    util.disable_protonmediaconverter()
