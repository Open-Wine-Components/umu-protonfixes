"""Game fix for Breath of Fire IV"""

from protonfixes import util

def main() -> None:
    """Load shipped dlls"""
    util.winedll_override("ddraw", "n,b") 
    util.winedll_override("dinput", "n,b") 
