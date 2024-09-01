"""Game fix for Crysis"""

from protonfixes import util


def main() -> None:
    """Installs d3dcompiler_43, disables esync"""

    # https://github.com/ValveSoftware/Proton/issues/178#issuecomment-422986182
    util.protontricks('d3dcompiler_43')

    # https://github.com/ValveSoftware/Proton/issues/178#issuecomment-415201326
    util.disable_esync()
