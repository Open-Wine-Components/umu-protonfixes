"""Mod support for Stellar Blade"""

import os
import glob
from protonfixes import util


def main() -> None:
    """Enable modding and fixes"""
    install_dir = glob.escape(util.get_game_install_path())

    # UE4SS
    if os.path.exists(install_dir + '/SB/Binaries/Win64/ue4ss'):
        util.winedll_override('dwmapi', util.OverrideOrder.NATIVE_BUILTIN)
