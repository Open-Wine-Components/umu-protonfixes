"""Game fix for Warhammer Vermintide II"""

from protonfixes import util


def main() -> None:
    """Fixes launcher constantly trying to install webview2"""
    # Fixes Content Manager (black windows)
    util.winedll_override('WebView2Loader', 'd')
