"""Load configuration settings for protonfixes"""

import re

from configparser import ConfigParser
from dataclasses import dataclass, is_dataclass
from pathlib import Path

from typing import Any
from collections.abc import Callable

from logger import log, LogLevelType

class ConfigBase:
    __CAMEL_CASE_PATTERN: re.Pattern = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')

    @classmethod
    def snake_case(cls, input: str) -> str:
        # Convert CamelCase to snake_case
        return cls.__CAMEL_CASE_PATTERN.sub(r'_\1', input).lower()


    @staticmethod
    def __log(message: str, level: LogLevelType = 'INFO') -> None:
        log.log(f'[CONFIG]: {message}', level)


    def __init__(self, path: Path) -> None:
        assert path
        if path.is_file():
            self.parse_config_file(path)
        elif not path.exists():
            self.init_sections()
            self.write_config_file(path)
        else:
            raise IsADirectoryError(f'Given path "{path.absolute()}" exists, but is not a file.')


    def init_sections(self, force: bool = False) -> None:
        for (member_name, member) in self.__class__.__dict__.items():
            # Find non private section definitions
            if not member_name.endswith('Section') or member_name.startswith('_'):
                continue
            if not is_dataclass(member):
                continue

            # Convert section definition class name to variable name (MyCfgSection -> my_cfg)
            section_name = member_name.removesuffix('Section')
            section_name = self.snake_case(section_name)

            # Do not override existing members by default
            if hasattr(self, section_name) and not force:
                continue

            # Initialize section class as a member
            setattr(self, section_name, member()) # pyright: ignore [reportCallIssue]


    def parse_config_file(self, file: Path) -> bool:
        # Initialize / reset sections to defaults
        self.init_sections(True)

        # Only precede if the config file exists
        if not file.is_file():
            return False

        try:
            parser = ConfigParser()
            parser.read(file)

            # Iterate over local config section objects
            for (section_name, section) in self.__dict__.items():
                if not parser.has_section(section_name):
                    continue

                parser_items = parser[section_name]

                # FIXME: match is not supported in Python 3.9
                def _get_parse_function(type_name: str) -> Callable[[str], Any]:
                    # Mapping of type_name to according value get function
                    value = {
                        'int': parser_items.getint,
                        'float': parser_items.getfloat,
                        'bool': parser_items.getboolean,
                        'Path': lambda option: Path(parser_items.get(option, '')),
                        'PosixPath': lambda option: Path(parser_items.get(option, '')),
                        'str': parser_items.get
                    }.get(type_name, None)
                    if not value:
                        value = parser_items.get
                        self.__log(f'Unknown type "{type_name}", falling back to "str".')
                    return value

                # Iterate over the option objects in this section
                for (option_name, option_item) in section.__dict__.items():
                    # Get values from config and set it on object
                    type_name = type(option_item).__name__
                    func = _get_parse_function(type_name)
                    value = func(option_name)
                    setattr(section, option_name, value)
        except Exception as ex:
            self.__log(f'Failed to parse config file "{file}". Exception: "{ex}"', 'CRIT')
            return False
        return True


    def write_config_file(self, file: Path) -> bool:
        # Only precede if the parent directory exists
        if not file.parent.is_dir():
            self.__log(f'Parent directory "{file.parent}" does not exist. Abort.', 'WARN')
            return False

        # Create and populate ConfigParser
        try:
            parser = ConfigParser()
            # Iterate over local config section objects
            for (section_name, section_item) in self.__dict__.items():
                if not parser.has_section(section_name):
                    parser.add_section(section_name)
                
                for (option_name, option_item) in section_item.__dict__.items():
                    parser.set(section_name, option_name, str(option_item))

            # Write config file
            with file.open(mode='w') as stream:
                parser.write(stream)
        except Exception as ex:
            self.__log(f'Failed to create config file "{file}". Exception: "{ex}"', 'CRIT')
            return False
        return True
