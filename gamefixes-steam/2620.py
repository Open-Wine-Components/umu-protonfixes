"""Game fix for Call of Duty (2003)"""

from protonfixes import util


def early() -> None:
    """Set Mesa env vars"""
    # https://github.com/ValveSoftware/Proton/pull/1423/commits/1a1d25c7d95691e37c94aea4e5f94e0c917aba6f
    util.set_environment('PROTON_OLD_GL_STRING', '1')
