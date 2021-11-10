""" Rainbow Six Siege
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Rainbow Six Siege needs vk_x11_override_min_image_count=2 for AMD
    """

    # https://github.com/ValveSoftware/Proton/issues/200#issuecomment-415905979
    util.set_environment('vk_x11_override_min_image_count', '2')
