"""Game fix for Duet Night Abyss"""

import os

from protonfixes import util


def _is_env_one(name: str) -> bool:
    return os.environ.get(name, '') == '1'


def early() ->  None:
    util.set_environment('PROTON_SET_GAME_DRIVE', '1')


def main() -> None:
    """CEF tries to use dcomp by default which only has stubs, this triggers a fallback to a different backend"""
    util.winedll_override('dcomp', util.OverrideOrder.DISABLED)

    """News tab freezes upon spawn on winewayland, disabling libGLES fixes it """
    if _is_env_one('PROTON_USE_WAYLAND') or _is_env_one('PROTON_ENABLE_WAYLAND'):
        util.winedll_override('libGLESv2', util.OverrideOrder.DISABLED)

    util.set_environment('PROTON_ENABLE_INT3_HACK', '1')
