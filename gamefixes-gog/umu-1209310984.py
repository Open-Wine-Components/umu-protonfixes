"""Game fix for Full Metal Daemon Muramasa"""

from protonfixes import util


def main() -> None:
    util.disable_protonmediaconverter()
    util.set_environment('PROTON_MEDIA_USE_GST', '1')
