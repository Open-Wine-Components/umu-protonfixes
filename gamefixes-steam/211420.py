"""Game fix Dark Souls Prepare To Die Edition"""

from pathlib import Path

from protonfixes import util

_DLL_OVERRIDES_KEY = r'HKEY_CURRENT_USER\Software\Wine\DllOverrides'


def _has_dsfix() -> bool:
    """Return whether DSfix installed a game-local dinput8 proxy."""
    data_dir = Path(util.get_game_install_path()) / 'DATA'
    if not data_dir.is_dir():
        return False

    return any(
        entry.is_file() and entry.name.casefold() == 'dinput8.dll'
        for entry in data_dir.iterdir()
    )


def main() -> None:
    """Use native dinput8 only for the optional DSfix proxy DLL."""
    if _has_dsfix():
        order = util.OverrideOrder.NATIVE_BUILTIN
        registry_order = 'native,builtin'
    else:
        order = util.OverrideOrder.BUILTIN
        registry_order = 'builtin'

    util.winedll_override('dinput8', order)
    util.regedit_add(
        _DLL_OVERRIDES_KEY, 'dinput8', 'REG_SZ', registry_order
    )
