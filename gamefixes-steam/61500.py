"""Game fix for Age of Wonders"""

from protonfixes import util


def main() -> None:
    # The game minimizes itself when it loses focus by hiding its main
    # window. On Wayland, nothing is left to restore it from, so it keeps
    # running in the background with only audio. Don't deactivate it when
    # the host keyboard focus leaves its window.
    util.set_environment('WAYLANDDRV_FOCUS_LOSS', '0')
