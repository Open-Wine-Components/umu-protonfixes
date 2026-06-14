"""Game fix for The Fruit of Grisaia (345610).

Fixes in-game graphics by setting ENABLE_GAMESCOPE_WSI=0 if run via gamescope.
Note, heuristics are applied, which can be spoofed, but suffices for now as a
robust solution for identifying gamescope would be more involved.
"""

import os
from pathlib import Path

from protonfixes import util


def main() -> None:
    if not os.environ.get('GAMESCOPE_WAYLAND_DISPLAY'):
        return

    # In steamrt4, pressure-vessel changes this value from gamescope-0 ->
    # /run/pressure-vessel/gamescope-socket.
    if not Path(os.environ['GAMESCOPE_WAYLAND_DISPLAY']).is_socket():
        return

    if os.environ.get('XDG_CURRENT_DESKTOP') != 'gamescope':
        return

    util.set_environment('ENABLE_GAMESCOPE_WSI', '0')
