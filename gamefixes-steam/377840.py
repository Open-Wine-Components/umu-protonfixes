"""Game fix for FINAL FANTASY IX"""

from protonfixes import util


def main() -> None:
    """Changes the proton argument from the launcher to the game"""
    # Fix crackling audio
    util.set_environment('PULSE_LATENCY_MSEC', '60')

    # Replace launcher with game exe in proton arguments
    util.replace_command('FF9_Launcher.exe', 'x64/FF9.exe')
