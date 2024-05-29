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


def check_material_config_file_code(new_config_file_path, new_material_code):
    with open(new_config_file_path) as f:
        new_config_material_code = f.readline().strip()[1:]  # Line is comment, starts with '#'
        if not re.match(MATERIAL_CODE_REGEX, new_config_material_code):
            print_error_and_exit(
                "Provided file does not start with a valid material code: %s\n" % new_config_material_code)

    if new_config_material_code != new_material_code:
        print_error_and_exit('File %s\'s material code %s does not match file name %s' % (new_config_file_path,
                                                                                          new_config_material_code,
                                                                                          new_material_code))


def backup_klipper_config_file():
    print('Backing up original config file \'%s\' to \'%s\'... ' %
          (PRINTER_CONFIG_FILE, klipper_config_backup_file_name),
          flush=True, end='')
    shutil.copyfile(PRINTER_CONFIG_FILE, klipper_config_backup_file_name)
    print('completed', flush=True)


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


def get_material_config_entry_line_index(file_contents):
    # Relative to klipper directory
    include_directive_regex = r"\[include " + \
                              material_directory_relative + r"\/" + \
                              MATERIAL_CODE_REGEX[:-1] + r".cfg\]"

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
    file_contents = read_file_content_as_lines(PRINTER_CONFIG_FILE)

    config_entry_line_index = get_material_config_entry_line_index(file_contents)

    if config_entry_line_index == -1:
        print_error_and_exit('Did not find any include directive in klipper config file %s! No changes were made!\n'
                             % PRINTER_CONFIG_FILE)

    file_contents[config_entry_line_index] = '[include %s/%s.cfg]\n' % (material_directory_relative, new_material_code)

    update_file_content(PRINTER_CONFIG_FILE, file_contents)


def clear_and_get_new_config_file_z_offset(new_config_file_location):
    file_contents = read_file_content_as_lines(new_config_file_location)
    z_endstop_entry_regex = r"([#])\s?(position_endstop_diff\s?=\s?([-]?\d*\.?\d+$))"
    z_endstop_entry_value = ''
    found_z_offset_entry = False
    compiled_regex = re.compile(z_endstop_entry_regex)

    offset_entry_line_index = -1
    for line in file_contents:
        offset_entry_line_index += 1
        regex_match = compiled_regex.match(line)
        if regex_match is not None:
            found_z_offset_entry = True
            z_endstop_entry_string = regex_match.groups()[1]
            z_endstop_entry_value = regex_match.groups()[2]
            # Invalid key for klipper, needs to be commented out
            file_contents[offset_entry_line_index] = '# ' + z_endstop_entry_string
            break

    if not found_z_offset_entry:
        return ''
    else:
        update_file_content(new_config_file_location, file_contents)
        return z_endstop_entry_value


def update_z_offset(new_config_file_location):
    z_offset_diff = clear_and_get_new_config_file_z_offset(new_config_file_location)
    if z_offset_diff == '':
        return
    gcode_command = 'SET_GCODE_OFFSET Z_ADJUST=%s' % z_offset_diff
    os.system("echo %s > %s" % (gcode_command, PRINTER_PIPE_FILE))
    print('Issuing gcode_command: ', gcode_command)


def update_config_file(new_material_code):
    if not file_exists(PRINTER_CONFIG_FILE):
        print_error_and_exit(print_error_and_exit('Printer config file %s does not exist!' % PRINTER_CONFIG_FILE))

    new_config_file_location = os.path.join(MATERIAL_DIRECTORY, new_material_code + '.cfg')
    if not file_exists(new_config_file_location):
        print_error_and_exit('Material configuration file %s does not exist!\n' % new_config_file_location)

    check_material_config_file_code(new_config_file_location, new_material_code)

    print("Switching to material: ", new_material_code)
    print("      New config file: ", new_config_file_location)
    print(flush=True)

    backup_klipper_config_file()

    update_z_offset(new_config_file_location)

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
    os.system("echo FIRMWARE_RESTART > %s" % PRINTER_PIPE_FILE)

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
