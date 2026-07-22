"""Game fix for Arknights: Endfield"""

import os
from protonfixes import util

def main() -> None:
    # Endfield will write large amounts of data while loading to LocalLow as mmapped files
    # these files appear to be jit code for worker threads as some form of ipc
    # no need for them to be on the disk and slow down loading, so symlink them to ram

    local_low = os.path.join(util.protonprefix(), 'drive_c/users/steamuser/AppData/LocalLow')
    for i in range(64):
        file = "HG_IL2CPP_MMAP" + str(i)
        if os.path.lexists(os.path.join(local_low, file)):
            os.remove(os.path.join(local_low, file))
        os.symlink(os.path.join("/dev/shm", file), os.path.join(local_low, file))
