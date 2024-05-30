import os
import re
import sys

import shutil
import logging

# You can use these entries to run this script locally using the GitHub provided folder structure
PRINTER_CONFIG_FILE = 'printer.cfg'
MATERIAL_DIRECTORY = 'MaterialSpecificConfigs'

# Absolute path, must be under your klipper config directory
# MATERIAL_DIRECTORY = '/home/fly/klipper_config/MaterialSpecificConfigs/'
# Absolute path
# PRINTER_CONFIG_FILE = '/home/fly/klipper_config/printer.cfg'
PRINTER_CONFIG_FILE_BACKUP_EXTENSION = '.bup'
MATERIAL_CODE_REGEX = r"[A-Z]{3}\d{3}$"
MATERIAL_CODE_REGEX_EXAMPLE = 'PLA001'  # Leave empty if you don't want to add an example
PRINTER_PIPE_FILE = '/tmp/printer'
# TODO - CHKA: Create class and move variables like this to an initialization phase
material_directory_relative = os.path.basename(os.path.normpath(MATERIAL_DIRECTORY))
klipper_config_backup_file_name = PRINTER_CONFIG_FILE + PRINTER_CONFIG_FILE_BACKUP_EXTENSION


def print_error_and_exit(error_message):
    sys.stderr.write(error_message)
    # Flushing because the G-Code Shell Command Extension context we're running under handles output differently
    sys.stderr.flush()
    sys.exit(-1)


def file_exists(new_config_file_location):
    return os.path.exists(new_config_file_location)


def handle_file_write_error(e):
    sys.stderr.write('Error! Writing to klipper config file %s failed!'
                     % PRINTER_CONFIG_FILE)
    logging.exception(e)

    if not file_exists(klipper_config_backup_file_name):
        print_error_and_exit('No backup file %s found! Check backup file extension. Aborting...' %
                             klipper_config_backup_file_name)

    sys.stderr.write('Attempting to recover from file %s\n' % klipper_config_backup_file_name)
    sys.stderr.flush()

    shutil.copyfile(klipper_config_backup_file_name, PRINTER_CONFIG_FILE)
    sys.exit(-1)


def update_file_content(printer_config_file, new_file_contents):
    try:
        klipper_config_file_write_stream = open(printer_config_file, 'w')
        klipper_config_file_write_stream.writelines(new_file_contents)
        klipper_config_file_write_stream.close()
    except Exception as e:
        logging.warning(e)
        sys.exit(1)


def read_file_content_as_lines(file_path):
    klipper_config_file_read_stream = open(file_path, 'r')
    file_contents = klipper_config_file_read_stream.readlines()
    klipper_config_file_read_stream.close()
    return file_contents


def print_material_code_regex():
    sys.stderr.write('Configured material code regex is of form %s\n' % MATERIAL_CODE_REGEX)
    if MATERIAL_CODE_REGEX_EXAMPLE != '':
        sys.stderr.write('Example: %s\n' % MATERIAL_CODE_REGEX_EXAMPLE)
    sys.stderr.flush()


def get_user_input_code(arguments):
    if len(arguments) < 2:
        print('Usage: %s <material code>' % arguments[0])
        print_material_code_regex()
        sys.exit(-1)

    user_input_code = sys.argv[1]

    # Step 1
    if not re.match(MATERIAL_CODE_REGEX, user_input_code):
        sys.stderr.write('Input code error \'%s\'! Please provide a valid material code\n' % user_input_code)
        print_material_code_regex()
        sys.exit(-1)

    return user_input_code
