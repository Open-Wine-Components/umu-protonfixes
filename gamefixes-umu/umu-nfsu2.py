"""Game fix for Need for Speed: Underground 2"""

from protonfixes import util


def main() -> None:
    """Limit to 1 CPU core, set dinput8 native then builtin (for widescreen patch), attach D: as CD-ROM drive"""
    util.set_cpu_topology_limit(1)
    util.winedll_override('dinput8', util.OverrideOrder.NATIVE_BUILTIN)
    util.create_dos_device(letter='d')
