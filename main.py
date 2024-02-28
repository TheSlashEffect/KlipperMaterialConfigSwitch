import os
import re
import sys
import csv

import shutil

MATERIAL_DIRECTORY = 'MaterialSpecificConfigs'
PRINTER_CONFIG_FILE = 'printer.cfg'


def change_config_file(new_material_code):
    new_config_file_location = MATERIAL_DIRECTORY + '/' + new_material_code + '.cfg'

    # Step 2: Check if file containing the desired code exists
    if not os.path.exists(new_config_file_location):
        sys.stderr.write('Material configuration file %s does not exist!\n' % new_config_file_location)
        sys.exit(-1)

    # Step 3: Check if file starts with a valid material code
    with open(new_config_file_location) as f:
        material_regex = '#[A-Z]{3}\d{3}$'
        new_config_material_code = f.readline().strip()
        if not re.match(material_regex, new_config_material_code):
            sys.stderr.write(
                "Provided file does not start with a valid material code: %s" % new_config_material_code)
            sys.exit(-1)

    if new_config_material_code[1:] != new_material_code:
        sys.stderr.write('File %s\'s material code %s does not match file name %s' % (new_config_file_location,
                                                                                      new_config_material_code[1:],
                                                                                      new_material_code))
        sys.exit(-1)

    print("Switching to material %s - Config file: %s" % (new_config_material_code[1:], new_config_file_location))

    # Step 4: Create backup of original configuration
    shutil.copyfile('printer.cfg', 'printer.cfg.bup')

    # Step 5: Modify printer.cfg
    with open('printer.cfg', 'r+') as f:
        include_directive_regex = '\[include ' + \
                                  MATERIAL_DIRECTORY + \
                                  '\/[A-Z]{3}\d{3}\.cfg\]'
        old = f.readlines()
        f.seek(0)
        for line in old:
            if re.match(include_directive_regex, line):
                f.write('[include %s/%s.cfg]\n' % (MATERIAL_DIRECTORY, new_material_code))
            else:
                f.write(line)


def printMaterialCodes():
    with open('index.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            print(', '.join(row))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: %s <material code>' % sys.argv[0])
        sys.exit()
    # input_code = 'PLA002'
    input_code = sys.argv[1]

    # Step 1
    input_material_regex = '[A-Z]{3}\d{3}$'
    if not re.match(input_material_regex, input_code):
        sys.stderr.write('Input code error \'%s\'! Please provide a valid material code' % input_code)
        # TODO - Print index.csv
        sys.exit(-1)

    change_config_file(input_code)

    # Step 7: Restart klipper (firmware restart)
    os.system("echo FIRMWARE_RESTART > /tmp/printer")

    '''
    Steps:
    1. Confirm that the new material code complies with the regex format (DONE)
    2. Check that a config file with the desired code exists (DONE)
    3. Confirm that the file we're reading starts with a regex compliant material code (DONE)
    4. Create backup of printer.cfg before altering it (printer.cfg.bup)
    5. Replace the existing printer.cfg entry to the new one
        using sed.
    6. Restart klipper
    
    Bonus: Create index file for codes. If user did not provide input code, print it out
    '''
