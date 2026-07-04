"""Game fix for Pajama Sam 4: Life is Rough When you Lose your Stuff!"""

#Copied over from Root Core's fix for Putt-Putt: Pep's Birthday Surprise (294700) (https://github.com/Root-Core)
#https://github.com/Open-Wine-Components/umu-protonfixes/blob/master/gamefixes-steam/294700.py

from protonfixes import util


def main() -> None:
    """The game doesn't run unless there is a CD-ROM drive attached."""
    util.create_dos_device()

    # sets up ID? exported from regedit
    util.regedit_add(
        'HKLM\\System\\MountedDevices',
        '\\??\\Volume{00000000-0000-0000-0000-000000000052}',
        'REG_BINARY',
        '2f746d7000',
    )

    # sets up dosdevice? exported from regedit
    util.regedit_add(
        'HKLM\\System\\MountedDevices',
        '\\DosDevices\\R:',
        'REG_BINARY',
        '5c005c002e005c0064003a000000',
    )
