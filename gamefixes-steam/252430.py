"""Game fix for Dusty Revenge: Co-Op Edition"""

from protonfixes import util


def main() -> None:
    """Install vcrun2010"""
    util.protontricks('vcrun2010')
    util.protontricks('dsound')
