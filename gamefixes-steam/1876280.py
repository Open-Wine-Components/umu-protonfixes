"""PAIcom"""

from protonfixes import util


def main() -> None:
    """Crashes unless dotnet48 is installed."""
    util.protontricks('dotnet48')
