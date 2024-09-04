"""Game fix for Call of Juarez: Gunslinger"""

from protonfixes import util


def main() -> None:
    """Fixes missing sound in cutscenes"""
    util.disable_protonmediaconverter()
