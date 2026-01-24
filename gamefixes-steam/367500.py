"""Game fix for Dragon's Dogma: Dark Arisen"""

from protonfixes import util


def main() -> None:
    """Dragon's Dogma: Dark Arisen (umu-367500, gog) requires SDL_JOYSTICK_HIDAPI="0", otherwise it becomes confused by the special inputs of a Dualsense 4 controller and will oscillate between Playstation, Xbox, Keyboard, and a Generic Gamepad layout mid-gameplay (it's very frustrating)."""
    util.set_environment('SDL_JOYSTICK_HIDAPI', '0')
