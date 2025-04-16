"""Game fix The Lord of the Rings Online"""

#
from protonfixes import util

import struct
import sys
import time
from Xlib.X import LASTEvent
from Xlib.display import Display
from Xlib.ext import xinput
from Xlib.protocol.request import GetProperty
from Xlib.xobject.drawable import Window


def is_window_focused(dpy: Display, window: Window) -> bool:
    """Returns True if the given window is currently focused (active)."""
    root = dpy.screen().root
    net_active_window = dpy.get_atom('_NET_ACTIVE_WINDOW')
    prop = root.get_full_property(net_active_window, 0)
    if not prop:
        return False
    return prop.value[0] == window.id


def get_window_name(dpy: Display, win: Window) -> GetProperty | None:
    """Retrieve the window name using WM_NAME or _NET_WM_NAME."""
    name = win.get_wm_name()
    if name:
        return name
    net_name = win.get_full_property(dpy.get_atom('_NET_WM_NAME'), 0)
    if net_name:
        return net_name.value.decode('utf-8')
    return None


def find_window_by_title(
    dpy: Display, title: str, win: Display | None = None
) -> Window | None:
    """Recursively find a window with a title containing the given string."""
    if win is None:
        win = dpy.screen().root
    name = get_window_name(dpy, win)
    if name and title in name:
        return win
    for child in win.query_tree().children:
        found = find_window_by_title(dpy, title, child)
        if found:
            return found
    return None


def get_game_window(dpy: Display, title: str) -> Window | None:
    game_window = None
    while game_window is None:
        game_window = find_window_by_title(dpy, title)
        if game_window is None:
            time.sleep(1)
    return game_window


def main() -> None:
    """Disable libglesv2"""
    ## gpu acelleration on wined3d https://bugs.winehq.org/show_bug.cgi?id=44985
    # Make the store work.
    util.winedll_override('libglesv2', 'd')

    title = 'The Lord of the Rings Online'
    dpy = Display()
    # Check if the XInput extension is available
    if not dpy.query_extension('XInputExtension'):
        raise RuntimeError('X Input Extension not available')
    # Initialize the XInput extension
    xinput_version = xinput.query_version(dpy)
    print('XInput version:', xinput_version.major_version, xinput_version.minor_version)
    # Wait for the game window to appear
    print(f"Waiting for window with title containing '{title}'...")
    game_window = get_game_window(dpy, title)
    print(f'Found game window: {get_window_name(dpy, game_window)}')
    dpy.screen().root.xinput_select_events(
        [
            (
                xinput.AllDevices,
                (1 << xinput.RawButtonPress) | (1 << xinput.RawButtonRelease),
            )
        ]
    )
    buttons_held = set()
    while True:
        if not is_window_focused(dpy, game_window):
            game_window = get_game_window(dpy, title)
            continue
        event = dpy.next_event()
        if event.type != LASTEvent or not hasattr(event, 'extension'):
            continue
        event_data = struct.unpack_from('HHHH', event.data)
        dpy.xfixes_query_version()
        # On button press
        if event.evtype == xinput.RawButtonPress:
            button = event_data[3]
            if button <= 3 and event_data[0] == 7:
                buttons_held.add(button)
                if len(buttons_held) == 1 and is_window_focused(dpy, game_window):
                    dpy.screen().root.xfixes_hide_cursor()
                    dpy.sync()
            continue

        # On button release
        elif event.evtype == xinput.RawButtonRelease:
            button = event_data[3]
            if button <= 3:
                buttons_held.discard(button)
                if len(buttons_held) == 0:
                    dpy.screen().root.xfixes_show_cursor()
                    dpy.sync()
            continue
