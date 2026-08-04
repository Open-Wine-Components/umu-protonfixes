"""Game fix for Dungeon Town.

The game loads its bundled fonts but requests two of them by PostScript name.
Install the NewRodin face that the game does not load itself, then alias both
PostScript names to the family names used by Wine.
"""

import shutil
from pathlib import Path

from protonfixes import util
from protonfixes.logger import log


FONT_KEYS = (
    'HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Fonts',
    'HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Fonts',
)
FONT_SUBSTITUTES_KEY = (
    'HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\FontSubstitutes'
)


def install_new_rodin() -> None:
    """Install the bundled NewRodin face that the game does not load."""
    font_name = 'FOT-NewRodinPro-DB.otf'
    source = Path(util.get_game_install_path()) / 'font' / font_name
    destination = util.protonprefix() / 'drive_c/windows/Fonts' / font_name

    if not source.is_file():
        log.warn(f'Could not find bundled font: {source}')
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.is_file():
        log.info(f'Installing bundled font: {font_name}')
        shutil.copy2(source, destination)

    for key in FONT_KEYS:
        util.regedit_add(key, 'NewRodinPro-DB', 'REG_SZ', font_name, arch=True)


def main() -> None:
    install_new_rodin()

    substitutions = {
        'NewRodinPro-DB': 'FOT-NewRodin Pro DB',
        'SourceHanSans-Medium': 'Source Han Sans Medium',
    }
    for postscript_name, family_name in substitutions.items():
        util.regedit_add(
            FONT_SUBSTITUTES_KEY,
            postscript_name,
            'REG_SZ',
            family_name,
            arch=True,
        )
