import os
import re
import sys

import common
import update_z_offset_use_case


class UpdateConfigUseCase:

    def __init__(self, new_config: common.Config):
        self.config = new_config

    def check_material_config_file_code(self, new_config_file_path, new_material_code):
        with open(new_config_file_path) as f:
            new_config_material_code = f.readline().strip()[1:]  # Line is comment, starts with '#'
            if not re.match(self.config.material_code_regex, new_config_material_code):
                common.print_error_and_exit(
                    "Provided file does not start with a valid material code: %s\n" % new_config_material_code)

        if new_config_material_code != new_material_code:
            common.print_error_and_exit('File %s\'s material code %s does not match file name %s'
                                        % (new_config_file_path,
                                           new_config_material_code,
                                           new_material_code))

    def get_material_config_entry_line_index(self, file_contents):
        # Relative to klipper directory
        include_directive_regex = r"\[include " + \
                                  self.config.material_directory_relative + r"\/" + \
                                  self.config.material_code_regex[:-1] + r".cfg\]"

        config_entry_line_index = -1
        for line in file_contents:
            config_entry_line_index += 1
            if re.match(include_directive_regex, line):
                print('Old material config file include entry: \n%s\n' % line, flush=True)
                break
        return config_entry_line_index

    # TODO - CHKA: Do not update file if new and existing entry match
    def update_klipper_config_material_entry(self, new_material_code):
        file_contents = common.read_file_content_as_lines(self.config.printer_config_file)
        config_entry_line_index = self.get_material_config_entry_line_index(file_contents)
        if config_entry_line_index == -1:
            common.print_error_and_exit('Did not find any include directive in klipper config file %s!'
                                        'No changes were made!\n'
                                        % self.config.printer_config_file)
        file_contents[config_entry_line_index] = '[include %s/%s.cfg]\n' % (
            self.config.material_directory_relative, new_material_code)
        common.update_file_content(config.printer_config_file, file_contents)

    def update_config_file(self, new_hardware_code):
        if not common.file_exists(self.config.printer_config_file):
            common.print_error_and_exit('Printer config file %s does not exist!' % self.config.printer_config_file)

        hardware_specific_config_file = str(os.path.join(self.config.material_directory, new_hardware_code + '.cfg'))
        if not common.file_exists(hardware_specific_config_file):
            common.print_error_and_exit(
                'Hardware configuration file %s does not exist!\n' % hardware_specific_config_file)

        self.check_material_config_file_code(hardware_specific_config_file, new_hardware_code)

        print("   Switching to hardware: ", new_hardware_code)
        print("New hardware config file: ", hardware_specific_config_file)
        print(flush=True)

        common.backup_klipper_config_file(self.config)

        self.update_klipper_config_material_entry(new_hardware_code)


if __name__ == '__main__':
    config = common.Config()
    input_code = common.get_user_input_code(config, sys.argv)
    config_updater = UpdateConfigUseCase(config)
    config_updater.update_config_file(input_code)

    z_offset_update_use_case = update_z_offset_use_case.VerticalOffsetUpdateUseCase(config)
    z_offset_update_use_case.update_z_offset(input_code)

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
