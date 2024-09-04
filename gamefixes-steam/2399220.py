"""Game fix for NUKITASHI"""

from protonfixes import util


def main() -> None:
    """Disable protonaudioconverterbin plugin"""
    # Fixes audio not playing for in-game videos
    util.disable_protonmediaconverter()
