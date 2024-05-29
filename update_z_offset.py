import os
import re
import sys
import logging

import common


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
        logging.warning(e)
        sys.exit(1)


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
            file_contents[offset_entry_line_index] = '# ' + z_endstop_entry_string + '\n'
            print('Found endstop diff = ', z_endstop_entry_value)
            break

    if not found_z_offset_entry:
        return ''
    else:
        update_file_content(new_config_file_location, file_contents)
        return z_endstop_entry_value


def issue_gcode_command(z_offset_diff):
    gcode_command = 'SET_GCODE_OFFSET Z_ADJUST=%s' % z_offset_diff
    os.system("echo %s > %s" % (gcode_command, common.PRINTER_PIPE_FILE))
    print('Issuing gcode_command: ', gcode_command)


def update_z_offset():
    input_code = 'PLA001'
    new_config_file_location = os.path.join(common.MATERIAL_DIRECTORY, input_code + '.cfg')
    z_offset_diff = clear_and_get_new_config_file_z_offset(new_config_file_location)
    if z_offset_diff == '':
        return
    issue_gcode_command(z_offset_diff)


if __name__ == '__main__':
    update_z_offset()
