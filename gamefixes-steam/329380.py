"""Game fix Stealth Inc 2: A Game of Clones"""

from protonfixes import util
from protonfixes.logger import log


def main() -> None:
    """Dsound is needed for audio"""
    log('Installing dsound')
    util.protontricks('dsound')
