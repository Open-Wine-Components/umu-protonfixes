"""Game fix for The Legend of Heroes: Trails in the Sky."""

from pathlib import Path

from protonfixes import util
from protonfixes.logger import log


DEFAULT_CONFIG = """[Video]
AdapterDX9=0
DeviceDX9=0
ModeDX9=4
WidthDX9=640
HeightDX9=480
RefreshRateDX9=0
FormatDX9=22
VendorIDDX9=4098
DeviceIDDX9=30032
KeepAspect=1
HardwareVertexShaderDX9=1
WindowMode=1
UseMipmap=0
WaitVSync=1
LowTexture=0
TextureFilter=2
FpsMode=0
FullAntiAlias=0
LowEffect=0
ShadowQuality=2
HighResoText=1
ForceTextReso=0
HighResoAssets=1
BoostFont=0
MinimapMode=1
StatusMode=1
Menu=0
LogoPlayOff=0
OpeningPlayOff=0
UseNewOrbmentLine=1
UseNewOrbmentLineStyle=1
[Sound]
BgmOff=0
SeOff=0
BgmVolume=6
SeVolume=6
NotUseDirectSound=0
NotUseDirectSound3d=0
BtVoiceOff=0
BtVoiceLang=0
SoftwareSoundBuffer=0
NoBeeping=0
BgmPack=0
[Control]
Camera45Deg=1
UseGamaPad=1
KeyboardUseDI=1
MouseUseDI=1
DefaultRun=0
ChrTrans=0
Analog=1
RightCamera=1
InvertCamera=0
LastAccessFile=121
ButtonMode=1
Keyboard=20111b41585a2628252742434d10564e12
GamePad=000108050403020907060a0b
PadDeviceNo=0
PadSensitivity=60
Mouse=0102
UseWheel=1
WheelReverse=0
RetryOffset=0
TurboLvField=2
TurboLvBattle=4
"""


def main() -> None:
    config_path = Path(util.get_game_install_path()) / 'SAVE' / 'config.ini'

    if config_path.exists():
        return

    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(DEFAULT_CONFIG, encoding='utf-8')
    except OSError as e:
        log.warn(f"Failed to create Trails in the Sky config at '{config_path}': {e}")
