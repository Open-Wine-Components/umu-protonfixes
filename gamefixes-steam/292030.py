"""Game fix for The Witcher 3: Wild Hunt

The 5.0 update looks up wine_get_version. When it finds it, the game never
initializes Streamline (DLSS SR/RR, DLSS-G, Reflex) and turns off ray tracing,
path tracing and FSR frame generation. Hide the Wine exports so it takes the
same path as on Windows.
"""

from protonfixes import util


def main() -> None:
    util.protontricks('hidewineexports=enable')

    # Without Wine, the game initializes NVAPI and retries in a loop when
    # dxvk-nvapi cannot, which hangs the menu on non-NVIDIA GPUs.
    # Same check as Proton's disablenvapi for this game.
    try:
        with open('/proc/modules', encoding='ascii') as f:
            drivers = {line.partition(' ')[0] for line in f.read().splitlines()}
    except OSError:
        drivers = set()
    if not drivers.intersection({'nvidia', 'nouveau', 'nova'}):
        util.disable_nvapi()
