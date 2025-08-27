"""Fable - The Lost Chapters"""

from protonfixes import util

def main() -> None:
    """Video Playback Fix"""
    util.set_environment('GST_GL_WINDOW', 'x11')
