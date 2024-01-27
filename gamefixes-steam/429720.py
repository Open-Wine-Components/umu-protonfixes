""" Game fix for IMSCARED
"""

#pylint: disable=C0103

from protonfixes import util
import os
import getpass

# IMSCARED relies on a folder on the user's Desktop being accessible
# The problem is that all of the folders in Proton are sandboxed
# So this protonfix works around that
def main():
    desktoppath = os.path.join(util.protonprefix(), 'drive_c/users/steamuser/Desktop')
    if os.path.exists(desktoppath):
        if os.path.islink(desktoppath):
    	    os.unlink(desktoppath)
        else:
    	    os.rmdir(desktoppath)
    dst = '/home/' + getpass.getuser() + '/Desktop/'
    os.symlink(dst, desktoppath)
	

