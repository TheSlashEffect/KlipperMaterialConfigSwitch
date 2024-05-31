# You can use these entries to run this script locally using the GitHub provided folder structure
# PRINTER_CONFIG_FILE = 'printer.cfg'
# modes = {'-m': 'MaterialSpecificConfigs', '-t': 'ToolheadSpecificConfigs'}

# Absolute path, must be under your klipper config directory
# MATERIAL_DIRECTORY = '/home/fly/klipper_config/MaterialSpecificConfigs/'
# Absolute path
PRINTER_CONFIG_FILE = '/home/fly/klipper_config/printer.cfg'
modes = {'-m': '/home/fly/klipper_config/MaterialSpecificConfigs',
         '-t': '/home/fly/klipper_config/ToolheadSpecificConfigs'}
PRINTER_CONFIG_FILE_BACKUP_EXTENSION = '.bup'
HARDWARE_CODE_REGEX = r"[A-Z]{3}\d{3}$"
HARDWARE_CODE_REGEX_EXAMPLE = 'PLA001'  # Leave empty if you don't want to add an example
PRINTER_PIPE_FILE = '/tmp/printer'
