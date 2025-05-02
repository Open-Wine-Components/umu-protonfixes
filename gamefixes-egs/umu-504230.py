"""Celeste"""
# EGS-ID Salt

from protonfixes import util


def main() -> None:
    util.set_environment('FNA3D_FORCE_DRIVER','OpenGL')
    # Vulkan is broken in the EGS build
