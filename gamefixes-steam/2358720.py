"""Game fix for Black Myth: Wukong"""

from protonfixes import util

def main() -> None:
    # Enable Hardware Scheduling for Frame Generation on Nvidia
    # https://github.com/jp7677/dxvk-nvapi/wiki/Tips-and-tricks-for-usage-with-DXVK-NVAPI#dlss-frame-generation
    # Causes the game to disable FSR on non-Nvidia GPUS, skip if not on Nvidia. Taken from Proton
    with open('/proc/modules') as f:
        drivers = set([line.partition(' ')[0] for line in f.read().splitlines()])
        if not drivers.intersection({'nvidia', 'nouveau', 'nova'}):
            util.regedit_delete(
                'HKLM\\System\\CurrentControlSet\\Control\\GraphicsDrivers',
                'HwSchMode'
            )
        else:
            util.regedit_add(
                'HKLM\\System\\CurrentControlSet\\Control\\GraphicsDrivers',
                'HwSchMode',
                'REG_DWORD',
                '2',
            )
