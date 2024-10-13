"""Load configuration settings for protonfixes"""

from config_base import ConfigBase
from dataclasses import dataclass
from pathlib import Path

class Config(ConfigBase):
    @dataclass
    class MainSection:
        enable_checks: bool = True
        enable_splash: bool = False
        enable_global_fixes: bool = True

    @dataclass
    class PathSection:
        cache_dir: Path = Path.home() / '.cache/protonfixes'

    main: MainSection
    path: PathSection

config = Config(Path.home() / '.config/protonfixes/config.ini')
