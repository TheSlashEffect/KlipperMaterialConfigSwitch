import os
import re
import sys

import shutil
import logging

import scriptConfig

from typing import List


class Config:

    # TODO - Use YAML file for config. Extra dependency to dissuade users???
    def initialize_from_config_file(self, mode: str) -> None:
        self.printer_config_file = scriptConfig.PRINTER_CONFIG_FILE
        self.hardware_directory = scriptConfig.modes[mode]
        self.hardware_directory_relative = os.path.basename(os.path.normpath(self.hardware_directory))
        self.printer_config_file_backup_extension = scriptConfig.PRINTER_CONFIG_FILE_BACKUP_EXTENSION
        self.hardware_code_regex = scriptConfig.HARDWARE_CODE_REGEX
        self.hardware_code_regex_example = scriptConfig.HARDWARE_CODE_REGEX_EXAMPLE
        self.printer_pipe_file = scriptConfig.PRINTER_PIPE_FILE

    def __init__(self, mode: str, hardware_code: str):
        self.printer_pipe_file = ''
        self.hardware_code_regex_example = ''
        self.hardware_code_regex = ''
        self.printer_config_file_backup_extension = ''
        self.hardware_directory = ''
        self.printer_config_file = ''
        self.hardware_directory_relative = ''
        self.initialize_from_config_file(mode)
        self.klipper_config_backup_file_name = (scriptConfig.PRINTER_CONFIG_FILE +
                                                scriptConfig.PRINTER_CONFIG_FILE_BACKUP_EXTENSION)
        self.hardware_code = hardware_code
        self.hardware_specific_config_file = str(os.path.join(self.hardware_directory,
                                                              hardware_code + '.cfg'))


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


def attempt_backup_recovery(config: Config) -> None:
    sys.stderr.write('Attempting to recover from file %s\n' % config.klipper_config_backup_file_name)
    sys.stderr.flush()

    shutil.copyfile(config.klipper_config_backup_file_name, config.printer_config_file)
    sys.exit(-1)


def handle_file_write_error(config: Config, e: Exception) -> None:
    sys.stderr.write('Error! Writing to klipper config file %s failed!'
                     % config.printer_config_file)
    logging.exception(e)

    if not file_exists(config.klipper_config_backup_file_name):
        print_error_and_exit('No backup file %s found! Check backup file extension. Aborting...' %
                             config.klipper_config_backup_file_name)

    attempt_backup_recovery(config)


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


def print_hardware_code_regex() -> None:
    sys.stderr.write('Configured hardware code regex is of form %s\n' % scriptConfig.HARDWARE_CODE_REGEX)
    if scriptConfig.HARDWARE_CODE_REGEX_EXAMPLE != '':
        sys.stderr.write('Example: %s\n' % scriptConfig.HARDWARE_CODE_REGEX_EXAMPLE)
    sys.stderr.flush()


def check_user_input_validity(hardware_mode: str, user_input_code: str):
    if hardware_mode not in scriptConfig.modes:
        print_error_and_exit('Invalid mode: %s\nAvailable modes:\n%s' %
                             (hardware_mode, str([i for i in scriptConfig.modes])))

    if not re.match(scriptConfig.HARDWARE_CODE_REGEX, user_input_code):
        sys.stderr.write('Input code error \'%s\'! Please provide a valid hardware code\n' % user_input_code)
        print_hardware_code_regex()
        sys.exit(-1)


def get_user_input_arguments(arguments: List[str]) -> tuple[str, str]:
    if len(arguments) < 3:
        print('Usage: %s {mode} {hardware_code}' % arguments[0])
        print_hardware_code_regex()
        sys.exit(-1)

    hardware_mode = arguments[1]
    user_input_code = arguments[2]
    check_user_input_validity(hardware_mode, user_input_code)

    return hardware_mode, user_input_code
