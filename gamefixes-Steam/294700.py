""" Game fix for Putt-Putt: Pep's Birthday Surprise
"""

#pylint: disable=C0103

from protonfixes import util
import os

# Putt-Putt: PBS doesn't run unless there is a CD-ROM drive attached.
def main():
    dosdevice = os.path.join(util.protonprefix(), 'dosdevices/r:')
    if not os.path.exists(dosdevice):
        os.symlink('/tmp', dosdevice) #create symlink for dosdevices

    util.regedit_add("HKLM\\System\\MountedDevices",'\\??\\Volume{00000000-0000-0000-0000-000000000052}','REG_BINARY','2f746d7000') #sets up ID? exported from regedit
    util.regedit_add("HKLM\\System\\MountedDevices",'\\DosDevices\\R:','REG_BINARY','5c005c002e005c0064003a000000') #sets up dosdevice? exported from regedit
    util.regedit_add("HKLM\\Software\\Wine\\Drives",'r:','REG_SZ','cdrom', 1) #designate drive as CD-ROM, requires 64-bit access
