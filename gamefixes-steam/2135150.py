"""Elin"""

from protonfixes import util


def main() -> None:
    """Fixes Steam Workshop modding."""
    util.winedll_override('winhttp', 'n,b')
