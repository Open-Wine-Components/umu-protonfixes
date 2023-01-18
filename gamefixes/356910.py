"""
Battle Fantasia Revised Edition

This game was designed to run at 60 fps (as most fighting games), but it
doesn't lock the frame rate in case your display refresh rate is higher
than 60Hz.

Related DXVK's issue: https://github.com/doitsujin/dxvk/issues/3145

"""
#pylint: disable=C0103
import os

def main():
    # only set the frame limit in case it is not already defined
    if "DXVK_FRAME_RATE" not in os.environ:
        os.environ["DXVK_FRAME_RATE"] = "60"

