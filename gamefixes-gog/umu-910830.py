"""Game fix for Rebel Galaxy Outlaw (GOG)"""

from protonfixes import util


def main() -> None:
    """Installs mfc42"""
    # GOG version has the same issue as Steam:
    # ScnLib.dll requires MFC42u.DLL which is not provided by Proton
    # https://github.com/ValveSoftware/Proton/issues/4216
    util.protontricks('mfc42')
