# Klipper Material/Hardware configuration switch macros

I wanted to be able to switch between filaments without having to adjust filament dependent
settings such as pid values, z offset (squish), etc. by hand.
Most people achieve all or part of this functionality using their slicer, but I wanted a solution that worked independently of 
the slicer used and would not depend on gcode file metadata.
The python script and configuration layout shown here achieve that with gcode macros and only one simple requirement utility.
This logic can be used to switch between other hardware as well, such as toolheads, nozzles, build surfaces, etc.
I want to keep this tool as dependency-free and user-friendly as possible, making it non-programmer friendly as well. If
you have the knowledge to set up klipper this will be more than doable.

![](images/browserViewFull.PNG "")
* Figure 1.1: Interface overview showing example macros

# Configuration file structure
Each material has its own configuration file.
We can choose what parameters change, such as hotend/bed temperature, 
pid values, or even things like minimum/maximum extrusion temperature.
Based on what parameters we choose this can also apply to
switching between toolheads, nozzles, build surfaces, etc.

![](images/materialConfigView.PNG "")
* Figure 1.2: Interface showing material specific configuration files

printer.cfg now imports this file as such:

`[include MaterialSpecificConfigs/PLA001.cfg]` 

Each material is identified by a material code. I write this code on the
spool with a sharpie, so I know which macro to use when I insert a new roll.
The default form is AAA999, but can be set in the "MATERIAL_CODE_REGEX" entry 
in _scriptConfig.py_. Config files are named `{MATERIAL_CODE}.cfg`,
and contain a comment with their material code in the first line, like so:

`#PLA001`

This is to ensure that we are not importing any files we did not mean to or edited by accident, and burning our house down in the process.

Any value in the config files also present in printer.cfg will be overwritten by the entry in 
the latter. Consult [LDO's guide on configuration read order](https://docs.ldomotors.com/en/guides/klipper_multi_cfg_guide#read-order)
if you want to change this behaviour in the script.

Take note that a backup of **printer.cfg** named **printer.cfg.bup** is created before the script modifies **printer.cfg**.

# Requirements:
- G-Code Shell Command Extension must be installed. 
For information on how to install please visit [kiauh's GitHub page](https://github.com/dw-0/kiauh/blob/master/docs/gcode_shell_command.md).

# Setup instructions:

  1. **BACK EVERYTHING UP!!! As with every extension that modifies your configuration directory,
it is recommended to fully back up your configuration directory before proceeding. And as 
always, USE AT YOUR OWN RISK! No guarantee comes with this software regarding safety.
Please review the code before using it!!!**

  2. Move whichever settings you change per material to a separate config file. You will need one config file for each material.
File import hierarchy can still be applied here, note how in my example in Figure 1.3 I have a separate file for the bed PID, which I reuse across 
material config files.

  3. Name each file **{MATERIAL_CODE}.cfg**, with the first line containing
a comment with the same material code, as shown in Figure 1.3. This is 
done to make sure we don't use files which we did not create manually for these purposes.
  4. (Optional) One can add a per-material z_offset value in the format shown below. This value is 
    an offset to the _position_endstop_ set in printer.cfg. To use this functionality, you must enable
    [save_variables](https://www.klipper3d.org/Config_Reference.html#save_variables) and add the following delayed
gcode macro in printer.cfg

    [delayed_gcode load_z_offset]
    initial_duration: 2
    gcode:
        {% set svv = printer.save_variables.variables %}
        SET_GCODE_OFFSET Z_ADJUST={svv.z_offset} MOVE=0

![](images/materialSpecificConfig.PNG "")
* Figure 1.3: Example of material specific config file


  4. Download all python scripts and place them in any directory. Take note of this path.

  5. Change "**MATERIAL_DIRECTORY**" in _scriptConfig.py_ to the directory containing your material specific configuration files,
     relative to klipper's main config directory.
     Change "**PRINTER_CONFIG_FILE**" to printer.cfg's location.

  6. In printer.cfg, add the following entry. This calls the driver script.
```cfg
[gcode_shell_command material_config_switch]
command: python3 {SCRIPT_LOCATION}/material_config_switch_use_case.py
```

  7. Create a macro for each material, as such
```cfg
[gcode_macro PLA001]
gcode:
    RUN_SHELL_COMMAND CMD=material_config_switch PARAMS=PLA001
```
where "PLA001" is the material code.

### Important!!!
  8. **Make sure to enable `Disabled while printing` in order to not accidentally run 
this and restart klipper mid-print.**

<img src="images/macroSettings.PNG" alt="drawing" width="500"/>

You can also assign a colour to the macro, so all your colours are shown in the browser.

![](images/macroBrowserView.PNG "")