"""Death end re;Quest"""

from protonfixes import util

def main() -> None:
    """Fixes performance and random crashings"""
    util.set_environment('WINE_CPU_TOPOLOGY', '2:0,1')