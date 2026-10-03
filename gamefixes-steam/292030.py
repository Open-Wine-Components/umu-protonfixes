"""Game fix for The Witcher 3: Wild Hunt

The 5.0 update looks up wine_get_version. When it finds it, the game never
initializes Streamline (DLSS SR/RR, DLSS-G, Reflex) and turns off ray tracing,
path tracing and FSR frame generation. Hide the Wine exports so it takes the
same path as on Windows.
"""

from protonfixes import util


def main() -> None:
    util.protontricks('hidewineexports=enable')
