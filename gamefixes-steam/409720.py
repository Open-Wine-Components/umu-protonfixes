"""Game fix for BioShock 2 Remastered"""

from protonfixes import util


def main() -> None:
    """Disable ESYNC and FSYNC"""

    # ESYNC and FSYNC causes low quality texture problems and frequent hangs.
    util.disable_esync()
    util.disable_fsync()
