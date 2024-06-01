import os
import re
import sys

import common
import update_z_offset_use_case

from typing import List


class UpdateConfigUseCase:

    def __init__(self, new_config: common.Config):
        self.config = new_config

    def check_hardware_config_file_validity(self, new_hardware_config_path: str) -> None:
        with open(new_hardware_config_path) as f:
            new_hardware_config_code = f.readline().strip()[1:]  # Line is comment, starts with '#'
            if not re.match(self.config.hardware_code_regex, new_hardware_config_code):
                common.print_error_and_exit(
                    "Provided file does not start with a valid hardware code: %s\n" % new_hardware_config_code)

        if new_hardware_config_code != config.hardware_code:
            common.print_error_and_exit('File %s\'s hardware code %s does not match file name %s'
                                        % (new_hardware_config_path,
                                           new_hardware_config_code,
                                           config.hardware_code))

    def get_hardware_config_entry_line_index(self, file_contents: List[str]) -> int:
        # Relative to main klipper config directory
        hardware_file_import_entry_regex = r"\[include " + \
                                           self.config.hardware_directory_relative + r"\/" + \
                                           self.config.hardware_code_regex[:-1] + r".cfg\]"
        found_import_directive = False
        config_entry_line_index = -1
        for line in file_contents:
            config_entry_line_index += 1
            if re.match(hardware_file_import_entry_regex, line):
                print('Old hardware config file include entry: \n%s\n' % line, flush=True)
                found_import_directive = True
                break
        return config_entry_line_index if found_import_directive else -1

    def update_klipper_config_hardware_entry(self, new_hardware_code: str) -> None:
        file_contents = common.read_file_content_as_lines(self.config.printer_config_file)
        config_entry_line_index = self.get_hardware_config_entry_line_index(file_contents)
        if config_entry_line_index == -1:
            common.print_error_and_exit('Did not find include directive for %s in klipper config file %s!\n'
                                        'No changes were made!\n'
                                        % (self.config.hardware_directory, self.config.printer_config_file))
        file_contents[config_entry_line_index] = '[include %s/%s.cfg]\n' % (
            self.config.hardware_directory_relative, new_hardware_code)
        common.update_file_content(config.printer_config_file, file_contents)

    def update_config_file(self) -> None:
        if not common.file_exists(self.config.printer_config_file):
            common.print_error_and_exit('Printer config file %s does not exist!' % self.config.printer_config_file)

        if not common.file_exists(config.hardware_specific_config_file):
            common.print_error_and_exit(
                'Hardware configuration file %s does not exist!\n' % config.hardware_specific_config_file)

        self.check_hardware_config_file_validity(config.hardware_specific_config_file)

        print("   Switching to hardware: ", config.hardware_code)
        print("New hardware config file: ", config.hardware_specific_config_file)
        print(flush=True)

        common.backup_klipper_config_file(self.config)

        self.update_klipper_config_hardware_entry(config.hardware_code)


if __name__ == '__main__':
    hardware_switch_option, hardware_code = common.get_user_input_arguments(sys.argv)
    config = common.Config(hardware_switch_option, hardware_code)
    config_updater = UpdateConfigUseCase(config)
    config_updater.update_config_file()

    z_offset_update_use_case = update_z_offset_use_case.VerticalOffsetUpdateUseCase(config)
    z_offset_update_use_case.update_z_offset()

    # Restart klipper
    os.system("echo FIRMWARE_RESTART > /tmp/printer")

    '''
    Steps:
    1. Confirm that the user provided hardware code complies with the regex format
    2. Check that a config file with the desired hardware code exists
    3. Confirm that said file starts with a regex compliant hardware code
    4. Create backup of printer.cfg before modifying it (ie. printer.cfg{PRINTER_CONFIG_FILE_BACKUP_EXTENSION})
    5. Update printer.cfg with new hardware config include directive
    6. Store z offset to printer's disk variables using SAVE_VARIABLE
    7. Restart klipper (firmware restart)
    
    TODO - CHKA: Create index file for codes. If user did not provide input code, print the file's contents
    '''
