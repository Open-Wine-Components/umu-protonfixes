"""Game fix for Soulbringer cd version"""

from protonfixes import util


def main() -> None:
    """Requires no-cd patch, disc does not get detected properly and keeps Wine hanging with sync:RtlpWaitForCriticalSection.
    Disable eax in advanced settings or the game won't run either.
    """
    util.protontricks('mfc42')
