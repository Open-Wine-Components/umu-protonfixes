"""Game fix for Indiana Jones and the Great Circle"""

from .. import util


def main() -> None:
	"""Bad performance on Nvidia due to poor VRAM utilization"""
	util.set_environment('DXVK_NVAPI_GPU_ARCH', 'GA100')
	util.set_environment('__GL_13ebad', '0x1')
