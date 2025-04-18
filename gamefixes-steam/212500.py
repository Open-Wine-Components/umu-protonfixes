"""Game fix The Lord of the Rings Online"""
import os
import subprocess
import sys

import struct
import time
from Xlib.X import LASTEvent
from Xlib.display import Display
from Xlib.ext import xinput
from Xlib.protocol.request import GetProperty
from Xlib.xobject.drawable import Window
from typing import Union


def is_window_focused(dpy: Display, window: Window) -> bool:
    """Returns True if the given window is currently focused (active)."""
    root = dpy.screen().root
    net_active_window = dpy.get_atom('_NET_ACTIVE_WINDOW')
    prop = root.get_full_property(net_active_window, 0)
    if not prop:
        return False
    return prop.value[0] == window.id


def get_window_name(dpy: Display, win: Window) -> Union[GetProperty, None]:
    """Retrieve the window name using WM_NAME or _NET_WM_NAME."""
    name = win.get_wm_name()
    if name:
        return name
    net_name = win.get_full_property(dpy.get_atom('_NET_WM_NAME'), 0)
    if net_name:
        return net_name.value.decode('utf-8')
    return None


def find_window_by_title(
        dpy: Display, title: str, win: Union[Display, None] = None
) -> Union[Window, None]:
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


def get_game_window(dpy: Display, title: str) -> Union[Window, None]:
    game_window = None
    retries = 0
    while game_window is None:
        game_window = find_window_by_title(dpy, title)
        if game_window is None:
            # give some time for the game window to open
            time.sleep(1)
            retries += 1
            if retries >= 30:
                print("Game window not found for 30 seconds, closing mouse fix.")
                # close display before exit
                dpy.close()
                exit()
    return game_window


def mouse_fix(title: str) -> None:
    # Check if there is a display
    if not os.getenv("DISPLAY", None):
        raise RuntimeError('No display detected')

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
    # detect button press and button release events
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
        event = dpy.next_event()
        if event.type != LASTEvent or not hasattr(event, 'extension'):
            continue
        event_data = struct.unpack_from('HHHH', event.data)
        dpy.xfixes_query_version()
        # On button press
        if event.evtype == xinput.RawButtonPress:
            button = event_data[3]
            if 1 <= button <= 3 and event_data[0] == 7:
                buttons_held.add(button)
                # only trigger hide_cursor when the first button is added to the set -> len(buttons_held) == 1
                # do not check for > 0, this will trigger the hide_cursor more than once when multiple buttons are
                # pressed and will hide the cursor forever unless the game is closed
                if len(buttons_held) == 1 and is_window_focused(dpy, game_window):
                    dpy.screen().root.xfixes_hide_cursor()
                    dpy.sync()
                elif not is_window_focused(dpy, game_window):
                    # get the new game window when we move from launcher to actual game window, they have the same name
                    game_window = get_game_window(dpy, title)
            continue

        # On button release
        elif event.evtype == xinput.RawButtonRelease:
            button = event_data[3]
            if 1 <= button <= 3:
                buttons_held.discard(button)
                if len(buttons_held) == 0:
                    dpy.screen().root.xfixes_show_cursor()
                    dpy.sync()
            continue


def main() -> None:
    # only import protonfixes here,
    # main_background function does not need it and also to prevent an error when this script is running as subprocess
    # bug in __init__.py check_conditions function ?
    #
    # 'waitforexitandrun' in sys.argv[1]
    # IndexError: list index out of range
    from protonfixes import util

    """Disable libglesv2"""
    ## gpu acelleration on wined3d https://bugs.winehq.org/show_bug.cgi?id=44985
    # Make the store work.
    util.winedll_override('libglesv2', 'd')

    # Fix visible mouse in middle of screen while rotating camera
    # This needs to run as a subprocess while the game is running,
    # the proces will close itself when the game window isn't detected for 30 seconds
    python_executable = sys.executable
    script_path = os.path.join(os.path.dirname(__file__), __file__)
    env = os.environ.copy()
    env['PYTHONPATH'] = sys.path[0]
    subprocess.Popen([python_executable, script_path],
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL,
                     stdin=subprocess.DEVNULL,
                     close_fds=True,
                     env=env)


def main_background():
    mouse_fix('The Lord of the Rings Online')


# triggered when this file is started as a subprocess
if __name__ == "__main__":
    sys.exit(main_background())
