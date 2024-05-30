import os
import re
import sys

import common


class VerticalOffsetUpdateUseCase:

    def __init__(self, new_config: common.Config):
        self.config = new_config

    def clear_and_get_new_config_file_z_offset(self):
        file_contents = common.read_file_content_as_lines(self.config.hardware_specific_config_file)
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
            common.update_file_content(self.config.hardware_specific_config_file, file_contents)
            return z_endstop_entry_value

    def issue_z_offset_store_command(self, z_offset_diff):
        gcode_command = 'SAVE_VARIABLE VARIABLE=z_offset VALUE=' + z_offset_diff
        os.system("echo %s > %s" % (gcode_command, self.config.printer_pipe_file))
        print('Issuing gcode_command to store z offset to gcode variable: ', gcode_command)

    def update_z_offset(self):
        z_offset_diff = self.clear_and_get_new_config_file_z_offset()
        if z_offset_diff == '':
            return
        self.issue_z_offset_store_command(z_offset_diff)


if __name__ == '__main__':
    hardware_code = common.get_user_input_code(sys.argv)
    config = common.Config(hardware_code)
    vertical_offset_update_use_case = VerticalOffsetUpdateUseCase(config)
    vertical_offset_update_use_case.update_z_offset()
