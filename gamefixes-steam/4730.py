"""Outrun 2006: Coast 2 Coast"""

from protonfixes import util


# Fix water rendering as black
def main() -> None:
    util.protontricks('d3dx9')
