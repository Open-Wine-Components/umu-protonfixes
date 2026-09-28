"""Game fix for Warframe
Will not launch without SteamDeck=0
Hide Wine exports to allow DX11 flip-model and HDR detection.
"""

from protonfixes import util


def main() -> None:
    util.set_environment('SteamDeck', '0')
    # The DX11 renderer skips flip-model and IDXGIOutput6 HDR detection when
    # wine_get_version is available, even with Optimized Flip-Model enabled.
    util.protontricks('hidewineexports=enable')
