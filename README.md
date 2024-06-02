# Klipper Material/Hardware configuration switch macros

These scripts allow switching between various hardware such as filaments without having to adjust hardware specific
settings such as pid values, z offset (squish), etc. by hand.
Most people achieve all or part of this functionality using their slicer, but I wanted a solution that worked independently of 
the slicer used and would not depend on gcode file metadata.

The python script and configuration layout shown here achieve that with gcode macros and only one simple requirement utility.
This logic can be used to switch between whatever hardware the user wants, such as toolheads, nozzles, build surfaces, etc.
The goal of this tool is to be as dependency-free and user-friendly as possible, making it non-programmer friendly as well. If
you have the knowledge to set up klipper this will be more than doable.

![](images/browserViewFull.PNG "")
* Figure 1.1: Interface overview showing example macros

# Configuration file structure
Each hardware has its own configuration file.
We can choose what parameters change, such as hotend/bed temperature, 
pid values, or even things like minimum/maximum extrusion temperature.
We can choose various different kinds of hardware to change with each macro, such as toolheads, nozzles, build surfaces, etc.\
For each such hardware we create a mode-directory pair in _scriptConfig.py_, as such:

    modes = {'-m': 'MaterialSpecificConfigs', '-b': 'BuildplateSpecificConfigs'}


![](images/materialConfigView.PNG "")
* Figure 1.2: Interface showing material specific configuration files

printer.cfg now imports files from each directory as such:

`[include MaterialSpecificConfigs/PLA001.cfg]` 

Each hardware, such as printing materials, is identified by a hardware code. I write this code on each
spool so I know which macro to use upon switching rolls.
The default form is AAA999, but can be set in the "HARDWARE_CODE_REGEX" entry 
in _scriptConfig.py_. Config files are named `{HARDWARE_CODE}.cfg`,
and contain a comment with their hardware code in the first line (Figure 1.3):
This is to ensure that we are not importing any files we did not mean to or edited by accident, and burning our house down in the process.

Any value in the config files also present in printer.cfg will be overwritten by the entry in 
the latter. Consult [LDO's guide on configuration read order](https://docs.ldomotors.com/en/guides/klipper_multi_cfg_guide#read-order).
The script modifies existing entries found for each hardware type (_MaterialSpecificConfigs_ in this example), 
so the import order you choose is kept the same.

Take note that a backup of **printer.cfg** named **printer.cfg.bup** is created before the script modifies **printer.cfg**.

# Requirements:
- G-Code Shell Command Extension must be installed. 
For information on how to install please visit [kiauh's GitHub page](https://github.com/dw-0/kiauh/blob/master/docs/gcode_shell_command.md).

# Setup instructions:

Before we start, **BACK EVERYTHING UP!!! As with every extension that modifies your configuration directory,
it is recommended to fully back up your configuration directory before proceeding. And as 
always, USE AT YOUR OWN RISK! No guarantee comes with this software regarding safety.
Please review the code before using it!!!**

  1. Move whichever settings you change per hardware to a separate config file.
Each file must be named **{HARDWARE_CODE}.cfg** and start with a comment containing said code (see Figure 1.3).
This is done to make sure we don't use files which we did not manually create for these purposes.
You will need one config file for each hardware/material.
File import hierarchy can still be applied here, note how in my example in Figure 1.3 I have separate files for the PID values,
which I reuse across material config files.

 ![](images/materialSpecificConfig.PNG "")
*Figure 1.3: Example of hardware specific config file for a PLA roll*



  2. (Optional) One can add a per-material z_offset value as shown above (`position_endstop_diff =  1.6`). This value is 
    an offset to the _position_endstop_ set in printer.cfg. To use this functionality, you must enable
    [save_variables](https://www.klipper3d.org/Config_Reference.html#save_variables) and add the following delayed
gcode macro in printer.cfg. This value is loaded upon klipper restart.

    [delayed_gcode load_z_offset]
    initial_duration: 2
    gcode:
        {% set svv = printer.save_variables.variables %}
        SET_GCODE_OFFSET Z_ADJUST={svv.z_offset} MOVE=0


  3. Download all python scripts and place them in any directory. Take note of this path.

  4. Add entries of the form `{mode, hardware_type}` items to the `modes` variable in _scriptConfig.py_ , where *mode* is an arbitrary name of your choice
and *hardware_type* being a hardware you want to switch between, in our example printing materials.
     Said paths are expressed relative to klipper's main config directory.
  5. In __printer.cfg__, add the following entries:
```cfg
# One initial value per hardware type you chose in scriptConfig.py
[include MaterialSpecificConfig/PLA001.cfg]
[include ToolheadSpecificConfig/TLH003.cfg]

# Call the driver script
[gcode_shell_command material_config_switch]
command: python3 {SCRIPTS_PATH}/material_config_switch_use_case.py

# Clear stored z_offset
[gcode_macro clear_z_offset]
gcode:
    SAVE_VARIABLE VARIABLE=z_offset VALUE=0
```
  6. Change "**PRINTER_CONFIG_FILE**" in _scriptConfig.py_ to printer.cfg's location.

  7. Create a macro for each hardware, as such
```cfg
[gcode_macro PLA001]
gcode:
    RUN_SHELL_COMMAND CMD=material_config_switch PARAMS="-m, PLA001"
```
where "m" is the mode and "PLA001" is the hardware code.

### Important!!!
**Make sure to disable the macro while a printjob is running. For example in fluidd, check `Disabled while printing`**

<img src="images/macroSettings.PNG" alt="drawing" width="500"/>

You can also assign a colour to the macro, so all your colours are shown in the browser.

![](images/macroBrowserView.PNG "")
