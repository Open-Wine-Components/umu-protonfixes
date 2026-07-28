"""Heroes Chronicles (Chapter 1-8)

These games come with a patched executable that loads a D3DCompat wrapper called 'xdd.dll' (shipped with the game). It,
however, does not run in Wine (crashing with a 0x6be exception). The games also come with a ..._og.exe executable, which
does not have this patch applied (and instead loads ddraw.dll), which works in Wine. Since it's easier to make further
compatibility fixes in Wine's ddraw implementation, let's just use the _og executables
"""

from protonfixes import util
from protonfixes.logger import log

EXECUTABLE_NAMES: dict[str, str] = {
    'umu-1207661743': 'Warlords',
    'umu-1207661753': 'Underworld',
    'umu-1207661763': 'Elements',
    'umu-1207661773': 'Dragons',
    'umu-1207661783': 'WorldTree',
    'umu-1207661793': 'FieryMoon',
    'umu-1207661803': 'Beastmaster',
    'umu-1207661813': 'Sword',
}

def main_with_id(game_id: str) -> None:
    exe_name = EXECUTABLE_NAMES.get(game_id)
    if exe_name is None:
        log.warn(f'Executed Heroes Chronicles fix on unknown game id: {game_id}')
        return

    util.replace_command(f'{exe_name}.exe', f'{exe_name}_og.exe')
