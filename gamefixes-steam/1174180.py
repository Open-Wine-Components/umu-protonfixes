"""Game fix for Red Dead Redemption 2"""

from protonfixes import util


def main() -> None:
    """Sometimes game will not launch if -fullscreen -vulkan is not specified"""
    util.append_argument('-fullscreen -vulkan')
