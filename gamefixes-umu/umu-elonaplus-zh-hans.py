"""Game fix for ElonaPlus(zh_Hans)

ElonaPlus(zh_Hans) is a translated version of ElonaPlus(https://wikiwiki.jp/elonaplus/). Starting with version 2.30, the game checks whether it is running in a Wine or virtual machine environment and refuses to run if so. This fix hides the Wine API so it is not detected and ensures that GB18030 characters are displayed correctly.
"""

from protonfixes import util

def main() -> None:
    util.protontricks('hidewineexports=enable')
    util.set_environment('LANG', 'zh_CN.UTF-8')
