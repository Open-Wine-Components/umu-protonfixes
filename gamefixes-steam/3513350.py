"""Wuthering Waves - ID 3513350
https://www.protondb.com/app/3513350
"""

from protonfixes import util


def main() -> None:
   """Video playback glitches in 2.1+ content
   This disables Proton mfplat at the cost
   of in-game experience for now.
   """
   util.winedll_override('mfplat', 'd')
   """In-game browser fix.
   """
   util.wineexe_override('KRSDKExternal', 'd')
