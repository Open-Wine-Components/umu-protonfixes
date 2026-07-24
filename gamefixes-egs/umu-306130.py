"""Fix for the Elder Scrolls Online"""

from protonfixes import util


def main() -> None:
    # The launcher is a webview, it does not open correctly without webview2 installed
    util.protontricks('webview2')
