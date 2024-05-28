import os
import re
import sys

import shutil
import logging

# Absolute path, must be under your klipper config directory
MATERIAL_DIRECTORY = 'MaterialSpecificConfigs/'
# MATERIAL_DIRECTORY = '/home/fly/klipper_config/MaterialSpecificConfigs/'
# Absolute path
# PRINTER_CONFIG_FILE = '/home/fly/klipper_config/printer.cfg'
PRINTER_CONFIG_FILE = 'printer.cfg'
PRINTER_CONFIG_FILE_BACKUP_EXTENSION = '.bup'
MATERIAL_CODE_REGEX = r"[A-Z]{3}\d{3}$"
MATERIAL_CODE_REGEX_EXAMPLE = 'PLA001'  # Leave empty if you don't want to add an example


def file_exists(new_config_file_location):
    return os.path.exists(new_config_file_location)


def check_material_config_file_code(new_config_file_path, new_material_code):
    with open(new_config_file_path) as f:
        new_config_material_code = f.readline().strip()[1:]
        if not re.match(MATERIAL_CODE_REGEX, new_config_material_code):
            sys.stderr.write(
                "Provided file does not start with a valid material code: %s" % new_config_material_code)
            sys.exit(-1)

    if new_config_material_code != new_material_code:
        sys.stderr.write('File %s\'s material code %s does not match file name %s' % (new_config_file_path,
                                                                                      new_config_material_code,
                                                                                      new_material_code))
        sys.exit(-1)


def backup_klipper_config_file():
    klipper_config_file_backup = PRINTER_CONFIG_FILE + PRINTER_CONFIG_FILE_BACKUP_EXTENSION
    print('Backing up %s to %s ' % (PRINTER_CONFIG_FILE, klipper_config_file_backup),
          flush=True)
    shutil.copyfile(PRINTER_CONFIG_FILE, klipper_config_file_backup)


def handle_file_write_error(e):
    sys.stderr.write('Writing to klipper config file %s failed!'
                     % PRINTER_CONFIG_FILE)
    logging.exception(e)
    sys.stderr.write('Attempting to recover from file %s\n' %
                     PRINTER_CONFIG_FILE + PRINTER_CONFIG_FILE_BACKUP_EXTENSION)
    sys.stderr.flush()
    sys.exit(-1)


# TODO - CHKA: Do not update file if new and existing entry match
def update_klipper_config_material_entry(new_material_code):
    # Relative to klipper directory
    material_directory_relative = os.path.basename(os.path.normpath(MATERIAL_DIRECTORY))
    include_directive_regex = r"\[include " + \
                              material_directory_relative + r"\/" + \
                              MATERIAL_CODE_REGEX[:-1] + r".cfg\]"

    klipper_config_file_read_stream = open(PRINTER_CONFIG_FILE, 'r')
    file_contents = klipper_config_file_read_stream.readlines()

    config_entry_line_index = -1
    for line in file_contents:
        config_entry_line_index += 1
        if re.match(include_directive_regex, line):
            print('Old material config file include entry: \n%s\n' % line, flush=True)
            break

    klipper_config_file_read_stream.close()

    if config_entry_line_index == -1:
        sys.stderr.write('Did not find any include directive in klipper config file %s! No changes were made!\n'
                         % PRINTER_CONFIG_FILE)
        sys.stderr.flush()
        sys.exit(-1)

    file_contents[config_entry_line_index] = '[include %s/%s.cfg]\n' % (material_directory_relative, new_material_code)

    try:
        klipper_config_file_write_stream = open(PRINTER_CONFIG_FILE, 'w')
        klipper_config_file_write_stream.writelines(file_contents)
        klipper_config_file_write_stream.close()
    except Exception as e:
        handle_file_write_error(e)


def update_config_file(new_material_code):
    new_config_file_location = MATERIAL_DIRECTORY + new_material_code + '.cfg'

    if not file_exists(new_config_file_location):
        sys.stderr.write('Material configuration file %s does not exist!\n' % new_config_file_location)
        sys.exit(-1)

    check_material_config_file_code(new_config_file_location, new_material_code)

    print("Switching to material: ", new_material_code)
    print("      New config file: ", new_config_file_location)
    print(flush=True)

    backup_klipper_config_file()

    update_klipper_config_material_entry(new_material_code)


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
        sys.stderr.write('Input code error \'%s\'! Please provide a valid material code\n' % input_code)
        print_material_code_regex()
        sys.exit(-1)

    return user_input_code


if __name__ == '__main__':
    input_code = get_user_input_code(sys.argv)

    update_config_file(input_code)

    # Restart klipper
    os.system("echo FIRMWARE_RESTART > /tmp/printer")

    '''
    Steps:
    1. Confirm that the user input material code complies with the regex format
    2. Check that a config file with the desired code exists
    3. Confirm that the file we're reading starts with a regex compliant material code
    4. Create backup of printer.cfg before modifying it (printer.cfg.bup)
    5. Update printer.cfg
    6. Restart klipper (firmware restart)
    
    Bonus: Create index file for codes. If user did not provide input code, print it out
    '''
