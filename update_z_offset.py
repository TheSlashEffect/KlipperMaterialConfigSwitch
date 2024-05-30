import os
import re
import sys

import common


class ZUpdater:

    def __init__(self, new_config: common.Config):
        self.config = new_config

    @staticmethod
    def clear_and_get_new_config_file_z_offset(new_config_file_location):
        file_contents = common.read_file_content_as_lines(new_config_file_location)
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
            common.update_file_content(config, file_contents)
            return z_endstop_entry_value

    @staticmethod
    def issue_z_offset_store_command(z_offset_diff):
        gcode_command = 'SAVE_VARIABLE VARIABLE=z_offset VALUE=' + z_offset_diff
        os.system("echo %s > %s" % (gcode_command, config.printer_pipe_file))
        print('Issuing gcode_command: ', gcode_command)

    def update_z_offset(self, argv):
        input_code = common.get_user_input_code(config, argv)
        new_config_file_location = os.path.join(config.material_directory, input_code + '.cfg')
        z_offset_diff = self.clear_and_get_new_config_file_z_offset(new_config_file_location)
        if z_offset_diff == '':
            return
        self.issue_z_offset_store_command(z_offset_diff)


if __name__ == '__main__':
    config = common.Config()
    z_offset_updater = ZUpdater(config)
    z_offset_updater.update_z_offset(sys.argv)
