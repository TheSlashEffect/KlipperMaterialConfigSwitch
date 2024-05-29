import os
import re
import sys

import shutil
import logging

import common


def print_error_and_exit(error_message):
    sys.stderr.write(error_message)
    # Flushing because the G-Code Shell Command Extension context we're running under handles output differently
    sys.stderr.flush()
    sys.exit(-1)


def file_exists(new_config_file_location):
    return os.path.exists(new_config_file_location)


def check_material_config_file_code(new_config_file_path, new_material_code):
    with open(new_config_file_path) as f:
        new_config_material_code = f.readline().strip()[1:]  # Line is comment, starts with '#'
        if not re.match(common.MATERIAL_CODE_REGEX, new_config_material_code):
            print_error_and_exit(
                "Provided file does not start with a valid material code: %s\n" % new_config_material_code)

    if new_config_material_code != new_material_code:
        print_error_and_exit('File %s\'s material code %s does not match file name %s' % (new_config_file_path,
                                                                                          new_config_material_code,
                                                                                          new_material_code))


def backup_klipper_config_file():
    print('Backing up original config file \'%s\' to \'%s\'... ' %
          (common.PRINTER_CONFIG_FILE, common.klipper_config_backup_file_name),
          flush=True, end='')
    shutil.copyfile(common.PRINTER_CONFIG_FILE, common.klipper_config_backup_file_name)
    print('completed', flush=True)


def handle_file_write_error(e):
    sys.stderr.write('Error! Writing to klipper config file %s failed!'
                     % common.PRINTER_CONFIG_FILE)
    logging.exception(e)

    if not file_exists(common.klipper_config_backup_file_name):
        print_error_and_exit('No backup file %s found! Check backup file extension. Aborting...' %
                             common.klipper_config_backup_file_name)

    sys.stderr.write('Attempting to recover from file %s\n' % common.klipper_config_backup_file_name)
    sys.stderr.flush()

    shutil.copyfile(common.klipper_config_backup_file_name, common.PRINTER_CONFIG_FILE)
    sys.exit(-1)


def get_material_config_entry_line_index(file_contents):
    # Relative to klipper directory
    include_directive_regex = r"\[include " + \
                              common.material_directory_relative + r"\/" + \
                              common.MATERIAL_CODE_REGEX[:-1] + r".cfg\]"

    config_entry_line_index = -1
    for line in file_contents:
        config_entry_line_index += 1
        if re.match(include_directive_regex, line):
            print('Old material config file include entry: \n%s\n' % line, flush=True)
            break
    return config_entry_line_index


def read_file_content_as_lines(file_path):
    klipper_config_file_read_stream = open(file_path, 'r')
    file_contents = klipper_config_file_read_stream.readlines()
    klipper_config_file_read_stream.close()
    return file_contents


def update_file_content(printer_config_file, new_file_contents):
    try:
        klipper_config_file_write_stream = open(printer_config_file, 'w')
        klipper_config_file_write_stream.writelines(new_file_contents)
        klipper_config_file_write_stream.close()
    except Exception as e:
        handle_file_write_error(e)


# TODO - CHKA: Do not update file if new and existing entry match
def update_klipper_config_material_entry(new_material_code):
    file_contents = read_file_content_as_lines(common.PRINTER_CONFIG_FILE)
    config_entry_line_index = get_material_config_entry_line_index(file_contents)
    if config_entry_line_index == -1:
        print_error_and_exit('Did not find any include directive in klipper config file %s! No changes were made!\n'
                             % common.PRINTER_CONFIG_FILE)
    file_contents[config_entry_line_index] = '[include %s/%s.cfg]\n' % (
        common.material_directory_relative, new_material_code)
    update_file_content(common.PRINTER_CONFIG_FILE, file_contents)


def update_config_file(new_material_code):
    if not file_exists(common.PRINTER_CONFIG_FILE):
        print_error_and_exit(
            print_error_and_exit('Printer config file %s does not exist!' % common.PRINTER_CONFIG_FILE))

    new_config_file_location = os.path.join(common.MATERIAL_DIRECTORY, new_material_code + '.cfg')
    if not file_exists(new_config_file_location):
        print_error_and_exit('Material configuration file %s does not exist!\n' % new_config_file_location)

    check_material_config_file_code(new_config_file_location, new_material_code)

    print("Switching to material: ", new_material_code)
    print("      New config file: ", new_config_file_location)
    print(flush=True)

    backup_klipper_config_file()

    update_klipper_config_material_entry(new_material_code)

    # Restart klipper
    os.system("echo FIRMWARE_RESTART > %s" % common.PRINTER_PIPE_FILE)


if __name__ == '__main__':
    input_code = get_user_input_code(sys.argv)

    update_config_file(input_code)

    '''
    Steps:
    1. Confirm that the user input material code complies with the regex format
    2. Check that a config file with the desired code exists
    3. Confirm that the file we're reading starts with a regex compliant material code
    4. Create backup of printer.cfg before modifying it (ie. printer.cfg{PRINTER_CONFIG_FILE_BACKUP_EXTENSION})
    5. Update printer.cfg
    6. Restart klipper (firmware restart)
    
    TODO - CHKA: Create index file for codes. If user did not provide input code, print the file's contents
    '''
