"""Game fix for Angelic Chaos: RE-BOOT!"""

from protonfixes import util


def main() -> None:
    util.disable_protonmediaconverter()
    util.set_environment('PROTON_MEDIA_USE_GST', '1')
    util.append_argument('-vomstyle=layer')
    # Refer to the ATRI -My Dear Moments- hack to fix media playback
    util.set_environment('SteamGameId', '1230140')
