"""Game fix for The Bureau: XCOM Declassified"""

from protonfixes import util


def main() -> None:
    """Disables esync and fsync"""
    # https://github.com/ValveSoftware/Proton/issues/797#issuecomment-955180056
    util.disable_esync()
    util.disable_fsync()
