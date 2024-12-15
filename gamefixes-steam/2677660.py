"""Game fix for Indiana Jones and the Great Circle"""

from protonfixes import util


def main() -> None:
	"""Workarounds for various graphics driver bugs encountered in this game"""
	# RadV: Missing textures and glowing eyes
	util.set_environment('radv_legacy_sparse_binding', 'true')
	util.set_environment('radv_zero_vram', 'true')
	util.set_environment('RADV_DEBUG', 'nodcc')
	# Nvidia: bad performance due to poor VRAM utilization
	util.set_environment('DXVK_NVAPI_GPU_ARCH', 'GA100')
	util.set_environment('__GL_13ebad', '0x1')
