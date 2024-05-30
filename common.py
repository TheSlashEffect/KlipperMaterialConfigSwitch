import os
import re
import sys

import shutil
import logging

import scriptConfig

from typing import List


class Config:

    # TODO - Use YAML file for config
    def initialize_from_config_file(self):
        self.printer_config_file = scriptConfig.PRINTER_CONFIG_FILE
        self.material_directory = scriptConfig.MATERIAL_DIRECTORY
        self.printer_config_file_backup_extension = scriptConfig.PRINTER_CONFIG_FILE_BACKUP_EXTENSION
        self.material_code_regex = scriptConfig.MATERIAL_CODE_REGEX
        self.material_code_regex_example = scriptConfig.MATERIAL_CODE_REGEX_EXAMPLE
        self.printer_pipe_file = scriptConfig.PRINTER_PIPE_FILE

    def __init__(self):
        self.printer_pipe_file = None
        self.material_code_regex_example = None
        self.material_code_regex = None
        self.printer_config_file_backup_extension = None
        self.material_directory = None
        self.printer_config_file = None
        self.initialize_from_config_file()
        self.material_directory_relative = os.path.basename(os.path.normpath(scriptConfig.MATERIAL_DIRECTORY))
        self.klipper_config_backup_file_name = (scriptConfig.PRINTER_CONFIG_FILE +
                                                scriptConfig.PRINTER_CONFIG_FILE_BACKUP_EXTENSION)


def print_error_and_exit(error_message: str) -> None:
    sys.stderr.write(error_message)
    # Flushing because the G-Code Shell Command Extension context we're running under handles output differently
    sys.stderr.flush()
    sys.exit(-1)


def backup_klipper_config_file(config: Config) -> None:
    print('Backing up original config file \'%s\' to \'%s\'... ' %
          (config.printer_config_file, config.klipper_config_backup_file_name),
          flush=True, end='')
    shutil.copyfile(config.printer_config_file, config.klipper_config_backup_file_name)
    print('completed', flush=True)


def file_exists(new_config_file_location: str) -> bool:
    return os.path.exists(new_config_file_location)


def handle_file_write_error(config: Config, e: Exception) -> None:
    sys.stderr.write('Error! Writing to klipper config file %s failed!'
                     % config.printer_config_file)
    logging.exception(e)

    if not file_exists(config.klipper_config_backup_file_name):
        print_error_and_exit('No backup file %s found! Check backup file extension. Aborting...' %
                             config.klipper_config_backup_file_name)

    sys.stderr.write('Attempting to recover from file %s\n' % config.klipper_config_backup_file_name)
    sys.stderr.flush()

    shutil.copyfile(config.klipper_config_backup_file_name, config.printer_config_file)
    sys.exit(-1)


def update_file_content(file_path: str, new_file_contents: List[str]) -> None:
    try:
        klipper_config_file_write_stream = open(file_path, 'w')
        klipper_config_file_write_stream.writelines(new_file_contents)
        klipper_config_file_write_stream.close()
    except Exception as e:
        logging.warning(e)
        sys.exit(1)


def read_file_content_as_lines(file_path: str) -> List[str]:
    klipper_config_file_read_stream = open(file_path, 'r')
    file_contents = klipper_config_file_read_stream.readlines()
    klipper_config_file_read_stream.close()
    return file_contents


def print_material_code_regex(config: Config) -> None:
    sys.stderr.write('Configured material code regex is of form %s\n' % config.material_code_regex)
    if config.material_code_regex_example != '':
        sys.stderr.write('Example: %s\n' % config.material_code_regex_example)
    sys.stderr.flush()


def get_user_input_code(config: Config, arguments: List[str]) -> str:
    if len(arguments) < 2:
        print('Usage: %s <material code>' % arguments[0])
        print_material_code_regex(config)
        sys.exit(-1)

    user_input_code = sys.argv[1]

    # Step 1
    if not re.match(config.material_code_regex, user_input_code):
        sys.stderr.write('Input code error \'%s\'! Please provide a valid material code\n' % user_input_code)
        print_material_code_regex(config)
        sys.exit(-1)

    return user_input_code
