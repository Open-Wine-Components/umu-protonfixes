"""Game fix for Star Citizen"""

from protonfixes import util


def main() -> None:
    """Patches libcuda & installs required dependencies"""

    # patch libcuda to workaround crashes related to DLSS
    # See: https://github.com/jp7677/dxvk-nvapi/issues/174#issuecomment-2227462795
    util.patch_libcuda()

    # RSI Launcher depends on powershell
    util.protontricks('powershell')
