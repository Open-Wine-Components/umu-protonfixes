"""Game fix for The Elder Scrolls Online"""

from protonfixes import util


def main() -> None:
    """Installs Microsoft Edge WebView2 Runtime required for the game launcher"""
    util.protontricks('webview2')
