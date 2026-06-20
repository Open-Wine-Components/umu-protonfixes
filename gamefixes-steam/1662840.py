"""Game fix for Parquet"""

from protonfixes import util


def main() -> None:
    util.append_argument('-vomstyle=layer')
