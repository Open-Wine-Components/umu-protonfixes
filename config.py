"""Load configuration settings for protonfixes"""
import os
from dataclasses import dataclass
from pathlib import Path

from .config_base import ConfigBase


base_config = Path(os.getenv('XDG_CONFIG_HOME', '~/.config')).expanduser()
base_cache = Path(os.getenv('XDG_CACHE_HOME', '~/.cache')).expanduser()


class Config(ConfigBase):
    """Configuration for umu-protonfix"""

    @dataclass
    class MainSection:
        """General parameters

        Attributes:
            enable_checks (bool): Run checks (`checks.py`) before the fix is executed.
            enable_global_fixes (bool): Enables included fixes. If deactivated, only local fixes (`~/.config/protonfixes/localfixes`) are executed.

        """

        enable_checks: bool = True
        enable_global_fixes: bool = True

    @dataclass
    class PathSection:
        """Path parameters

        Attributes:
            cache_dir (Path): The path that should be used to create temporary and cached files.

        """

        cache_dir: Path = base_cache / 'protonfixes'

    main: MainSection
    path: PathSection


config = Config(base_config / 'protonfixes/config.ini')
