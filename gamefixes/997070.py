""" Game fix Marvel's Avengers
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    # Requires vcrun2019 to launch
    util.protontricks('vcrun2019_ge')
    util.protontricks('d3dcompiler_47')
    util.use_seccomp()
    util.set_environment('PROTON_NO_D3D12','1')
    util.set_environment('WINEDLLOVERRIDES','dxgi=n')


 
