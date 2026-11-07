"""Game fix for Cry of Fear"""

from protonfixes import util


def main() -> None:
    # The game ships a wrapper opengl32.dll ("PARANOIA_HACKS_V1") that its custom
    # renderer needs. Without it the flashlight, phone light and dynamic lights
    # do not work ("No paranoia hacked opengl32.dll, custom renderer disabled").
    util.winedll_override('opengl32', util.OverrideOrder.NATIVE_BUILTIN)
