"""Game fix for Ultima Online"""

from protonfixes import util


def main() -> None:
    # ClassicUO Launcher is a Tauri app and needs the WebView2 runtime
    util.protontricks('webview2')
