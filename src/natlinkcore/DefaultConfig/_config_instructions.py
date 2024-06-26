"""module that is loaded when no config file is found elsewhere

It gives the instructions for a correct place to put natlink.ini in
"""
import os
import os.path
from natlinkcore import config

join, expanduser, getenv = os.path.join, os.path.expanduser, os.getenv
isfile, isdir = os.path.isfile, os.path.isdir
home = expanduser('~')

this_dir, this_filename = __file__.rsplit('\\', 1)
if this_dir.find('\\site-packages\\') == -1:
    print(f'Working with symlinks! Working from directory: "{this_dir}"\n')

natlink_settingsdir = getenv("NATLINK_SETTINGSDIR")
natlink_userdir = getenv("NATLINK_USERDIR")

if natlink_settingsdir:
    natlink_settings_path = config.expand_path(natlink_settingsdir)
    if os.path.isdir(natlink_settings_path):
        if natlink_settingsdir == natlink_settings_path:
            print(f'You specified for NATLINK_SETTINGSDIR: "{natlink_settingsdir}"')
        else:
            print(f'You specified for NATLINK_SETTINGSDIR: "{natlink_settingsdir}", which expands to: "{natlink_settings_path}".')
            
if natlink_userdir:
    natlink_user_path = config.expand_path(natlink_userdir)
    
    if natlink_settingsdir:
        print(f'WARNING: You also specified NATLINK_USERDIR to "{natlink_userdir}", this setting is ignored.')
    else:
        print(f'WARNING: The setting of environment variable NATLINK_USERDIR (to "{natlink_userdir}") is obsolete,')
        print('please change this setting to NATLINK_SETTINGSDIR')
        
        


print(f'\n\n'
    f'\nThis is the file "{this_filename}" from directory "{this_dir}".'
    f'\nThis directory holds the default "natlink.ini" file, when it is not found the default or configured directory.'
    f'\n\n'
    rf'The default directory is: "~\.natlink", with "~" being your HOME directory: "{home}".'
    f'\tSo: "{home}\\.natlink"'
    f"\n"
    f'\nThere is also a custom way to configure the directory of your "natlink.ini" file:'
    f'\n'
    f'\nSpecify the environment variable "NATLINK_SETTINGSDIR", which should point to an existing directory.'
    f'\nNote: this directory may NOT be a shared directory, like Dropbox or OneDrive.'
    f'\nSeveral directories to be configured may be shared however, but others must be local, which is hopefully '
    f'\nensured well enough in the config program.'
    f'\n'
    f'\nWhen this directory does not hold the file "natlink.ini",\nyou can copy it from "{this_dir}",'
    f'\nor (easier) run the configure program of Natlink, see below.'
    f'\n'
    f'\n\tWhen you run this program, the default version of "natlink.ini" will be copied into'
    f'\n\t *the correct place, and you can proceed with configuring'
    f'\n\tthe additional options in order to get started with using Natlink.'
    f'\n' )

if natlink_settingsdir:
    if os.path.isdir(natlink_settings_path):
        if natlink_settingsdir == natlink_settings_path:
            print(f'You specified for NATLINK_SETTINGSDIR: "{natlink_settingsdir}"')
        else:
            print(f'You specified for NATLINK_SETTINGSDIR: "{natlink_settingsdir}", which expands to: "{natlink_settings_path}".')
    else:
        print(f'You specified for NATLINK_SETTINGSDIR: "{natlink_settingsdir}", which does not expand to a valid directory: "{natlink_settings_path}".')
    print('The NATLINK_SETTINGSDIR should hold a valid config file "natlink.ini"')
else:
    print('The default config directory NATLINK_SETTINGSDIR should hold a valid config file "natlink.ini"')

msg = '\n'
'\nPlease try to run the config program (Command Line Interface) by running'
'\n***"Configure Natlink via GUI"*** or ***"Configure Natlink via CLI"***'
'\n\tfrom the Windows command prompt.'
'\n'
'\nAfter all these steps, (re)start Dragon and good luck...\n\n\n'

print(msg)
