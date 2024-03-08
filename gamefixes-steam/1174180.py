""" Game fix for Red Dead Redemption 2
"""
#pylint: disable=C0103
from protonfixes import util

def main():
    """ Sometimes game will not launch if -fullscreen -vulkan is not specified
    """
    util.append_argument('-fullscreen -vulkan')
    # Set SteamGameId so that non-steam versions can pick up steam-specific fixes in proton's wine code
    util.set_environment('SteamGameId','1174180')
