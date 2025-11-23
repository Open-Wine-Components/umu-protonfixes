"""Game fix for Black Myth: Wukong"""

from protonfixes import util

def main() -> None:
    # Enable Hardware Scheduling for Frame Generation on Nvidia
    # https://github.com/jp7677/dxvk-nvapi/wiki/Tips-and-tricks-for-usage-with-DXVK-NVAPI#dlss-frame-generation
    util.regedit_add(
        'HKLM\\System\\CurrentControlSet\\Control\\GraphicsDrivers',
        'HwSchMode',
        'REG_DWORD',
        '2',
    )
