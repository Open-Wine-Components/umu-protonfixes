"""Game fix for Senren*Banka"""

from protonfixes import util


def main() -> None:
    # Fixes audio stutters for in-game videos
    util.append_argument('-vomstyle=layer')
