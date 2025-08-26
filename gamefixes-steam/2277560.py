"""Mod support for Wuchang"""

import os
import glob
from protonfixes import util


def main() -> None:
    install_dir = glob.escape(util.get_game_install_path())

    """UE4SS"""
    if os.path.exists(install_dir + '/Project_Plague/Binaries/Win64/ue4ss'):
        util.winedll_override('dwmapi', util.OverrideOrder.NATIVE_BUILTIN)

    """Wuchang Mod Enabler"""
    if os.path.exists(install_dir + '/Project_Plague/Binaries/Win64/bitfix'):
        util.winedll_override('dsound', util.OverrideOrder.NATIVE_BUILTIN)
