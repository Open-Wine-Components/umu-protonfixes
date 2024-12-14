"""Rainbow Six Siege"""

from protonfixes import util


def main() -> None:
    """Rainbow Six Siege needs vk_x11_override_min_image_count=2 for AMD"""
    util.set_environment('vk_x11_override_min_image_count', '2')
