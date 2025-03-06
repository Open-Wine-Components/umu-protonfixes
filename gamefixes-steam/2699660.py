"""PowerWash Adventure"""

from protonfixes import util


def main() -> None:
    """Needs vcrun2019 to fix 'Visual C++ Runtime' required error"""
    util.protontricks('vcrun2022')
