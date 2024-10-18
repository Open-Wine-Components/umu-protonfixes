"""Game fix for Disgaea 4 Complete+"""

from protonfixes import util

def main() -> None:
	"""Usually won't reach menu unless Esync and Fsync are disabled"""
	util.disable_esync()
	util.disable_fsync()
