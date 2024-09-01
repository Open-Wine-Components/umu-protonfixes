"""Necromunda: Hired Gun"""

from protonfixes import util


def main() -> None:
    util.replace_command(
        'Necromunda.exe', 'Necromunda/Binaries/Win64/Necromunda-Win64-Shipping.exe'
    )
