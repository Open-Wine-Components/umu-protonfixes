"""Game fix for Borderlands: The Pre-Sequel"""

from protonfixes import util


def main() -> None:
    """Launcherfix and NVIDIA PhysX support."""
    # Fixes the startup process.
    util.replace_command('Launcher.exe', 'BorderlandsPreSequel.exe')
    util.append_argument('-NoSplash')

    # Disables esync prevents crashes.
    util.disable_esync()

    # Enables NVIDIA PhysX in Borderlands: The Pre-Sequel.
    util.protontricks('physx')
