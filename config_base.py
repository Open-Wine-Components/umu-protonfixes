"""Load configuration settings for protonfixes"""

import re

from configparser import ConfigParser
from dataclasses import is_dataclass
from pathlib import Path

from logger import log

class ConfigBase:
    __CAMEL_CASE_PATTERN: re.Pattern = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')

    @classmethod
    def snake_case(cls, input: str) -> str:
        # Convert CamelCase to snake_case
        return cls.__CAMEL_CASE_PATTERN.sub(r'_\1', input).lower()


    @staticmethod
    def __log(message: str, level: str = 'INFO') -> None:
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
            setattr(self, section_name, member())


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

                # Iterate over the option objects in this section
                for (option_name, option_item) in section.__dict__.items():
                    # Match type of local object
                    match type(option_item).__name__:
                        case 'int':
                            setattr(section, option_name, parser_items.getint(option_name))
                        case 'float':
                            setattr(section, option_name, parser_items.getfloat(option_name))
                        case 'bool':
                            setattr(section, option_name, parser_items.getboolean(option_name))
                        case 'Path':
                            setattr(section, option_name, Path(parser_items.get(option_name)))
                        case 'PosixPath':
                            setattr(section, option_name, Path(parser_items.get(option_name)))
                        case 'str':
                            setattr(section, option_name, parser_items.get(option_name))
                        case _:
                            setattr(section, option_name, parser_items.get(option_name))
                            self.__log(f'Type mismatch')
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
