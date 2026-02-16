"""Game fix for Akiba's Trip: Undead & Undressed"""

from protonfixes import util


def main() -> None:
    util.protontricks('hidewineexports=enable')
    util.set_environment('PROTON_MEDIA_USE_GST', '1')
