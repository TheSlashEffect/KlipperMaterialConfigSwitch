import os
import re
import sys

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
