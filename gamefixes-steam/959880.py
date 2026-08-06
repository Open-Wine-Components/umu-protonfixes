"""Game fix for Dungeon Town.

The game loads Source Han Sans but requests it by PostScript name. Alias that
name to the family name used by Wine. Force Wine's font-name selection to use
its English fallback because regional English locales can discard the Japanese
family aliases embedded in the game's other fonts.
"""

from protonfixes import util


FONT_SUBSTITUTES_KEY = (
    'HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\FontSubstitutes'
)


def main() -> None:
    util.set_environment('LC_ALL', 'C.UTF-8')
    util.regedit_add(
        FONT_SUBSTITUTES_KEY,
        'SourceHanSans-Medium',
        'REG_SZ',
        'Source Han Sans Medium',
        arch=True,
    )
