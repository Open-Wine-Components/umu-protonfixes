"""Game fix for Stronghold Crusader HD
Fixes Multiplayer, the too fast cursor and the tiny cursor on large displays
"""

import os
import re

from protonfixes import util

# The game ties its speed (cursor and scrolling included) to a 60 Hz vertical blank.
GAME_TICKS = '60'

# Cursors are 32x32 pixels. They only look tiny on large, high-resolution panels,
# so the cursor is enlarged only when the display is at least this tall.
CURSOR_SCALE_MIN_HEIGHT = 1440
CURSOR_SCALE = '2.5'


def get_display_height(drm_path: str = '/sys/class/drm') -> int:
    """Height in pixels of the preferred mode of the first connected display, 0 if unknown"""
    try:
        for card in sorted(os.listdir(drm_path)):
            status = os.path.join(drm_path, card, 'status')
            modes = os.path.join(drm_path, card, 'modes')
            if not (os.path.isfile(status) and os.path.isfile(modes)):
                continue
            with open(status, encoding='utf-8') as file:
                if file.read().strip() != 'connected':
                    continue
            with open(modes, encoding='utf-8') as file:
                match = re.match(r'(\d+)x(\d+)', file.readline().strip())
            if match:
                return int(match.group(2))
    except OSError:
        pass
    return 0


def main() -> None:
    """Installs directplay, limits the game tick rate and enlarges the cursor on large displays"""
    util.protontricks('directplay')

    # Run the game at 60 ticks per second instead of the refresh rate of the display
    # (needs the ddraw WINE_DDRAW_MAXGAMETICKS patch). Set the same variable in the
    # launch options to override.
    if 'WINE_DDRAW_MAXGAMETICKS' not in os.environ:
        util.set_environment('WINE_DDRAW_MAXGAMETICKS', GAME_TICKS)

    # Enlarge the cursor on large displays only (needs the winex11 WINE_CURSOR_SCALE patch).
    # Set the same variable in the launch options to override.
    if 'WINE_CURSOR_SCALE' not in os.environ and get_display_height() >= CURSOR_SCALE_MIN_HEIGHT:
        util.set_environment('WINE_CURSOR_SCALE', CURSOR_SCALE)
