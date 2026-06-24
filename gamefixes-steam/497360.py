"""Gabriel Knight 3: Blood of the Sacred, Blood of the Damned
Fix for Insert CD
Fixes graphical issues
Widescreen supported (16:9/21:9, 32:9 not tested)
"""

from protonfixes import util


def main() -> None:
    # use wined3d for now, d7vk flickers with this game
    #util.set_environment('PROTON_USE_D7VK', '1')

    # Create a symlink in dosdevices
    util.create_dos_device()

    # Get width of resolution
    resolution = util.get_resolution()
    if not resolution:
        return None

    screen_width, screen_height = resolution
    if not screen_height:
        return

    width = int(screen_width / screen_height * 768)

    # Registry
    util.regedit_add('HKCU\\Software\\Sierra On-Line')
    util.regedit_add('HKCU\\Software\\Sierra On-Line\\Gabriel Knight 3')
    util.regedit_add(
        'HKCU\\Software\\Sierra On-Line\\Gabriel Knight 3\\App',
        'Run Count',
        'REG_DWORD',
        '0x1',
    )
    util.regedit_add(
        'HKCU\\Software\\Sierra On-Line\\Gabriel Knight 3\\Engine',
        'Full Screen',
        'REG_DWORD',
        '0x1',
    )
    util.regedit_add(
        'HKCU\\Software\\Sierra On-Line\\Gabriel Knight 3\\Engine',
        'Monitor',
        'REG_DWORD',
        '0x0',
    )
    util.regedit_add(
        'HKCU\\Software\\Sierra On-Line\\Gabriel Knight 3\\Engine',
        'Rasterizer',
        'REG_SZ',
        'detect',
    )
    util.regedit_add(
        'HKCU\\Software\\Sierra On-Line\\Gabriel Knight 3\\Engine',
        'Rasterizer GUID',
        'REG_SZ',
        '{00000000-0000-0000-0000-000000000000}',
    )
    util.regedit_add(
        'HKCU\\Software\\Sierra On-Line\\Gabriel Knight 3\\Engine',
        'Screen Height',
        'REG_DWORD',
        '0x300',
    )
    util.regedit_add(
        'HKCU\\Software\\Sierra On-Line\\Gabriel Knight 3\\Engine',
        'Screen Width',
        'REG_DWORD',
        hex(width),
    )
    util.regedit_add(
        'HKCU\\Software\\Sierra On-Line\\Gabriel Knight 3\\Engine\\Hardware',
        'Gamma',
        'REG_SZ',
        '1.5',
    )
    util.regedit_add(
        'HKCU\\Software\\Sierra On-Line\\Gabriel Knight 3\\Engine\\Hardware',
        'Surface Quality',
        'REG_SZ',
        'High',
    )
