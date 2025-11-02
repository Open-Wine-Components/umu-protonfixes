"""Game fix for Genshin Impact"""

from protonfixes import util


def main() -> None:
    """Installs openal as redistributable install script is borked."""
    util.set_environment('UMU_USE_STEAM', '1')
