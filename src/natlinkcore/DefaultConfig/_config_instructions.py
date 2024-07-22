"""module that is loaded when no config file is found elsewhere

It gives the instructions for a correct place to put natlink.ini in
"""
import os
import os.path
from natlinkcore import config

join, expanduser, getenv, normpath = os.path.join, os.path.expanduser, os.getenv, os.path.normpath
isfile, isdir = os.path.isfile, os.path.isdir
home = expanduser('~')

this_dir, this_filename = __file__.rsplit('\\', 1)
if this_dir.find('\\site-packages\\') == -1:
    print(f'Working with symlinks! Working from directory: "{this_dir}"\n')

natlink_settingsdir = getenv("NATLINK_SETTINGSDIR")
natlink_userdir = getenv("NATLINK_USERDIR")

if natlink_settingsdir:
    natlink_settingsdir = normpath(natlink_settingsdir)
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
    f'\nThis directory holds the default "natlink.ini" file, when it is not found in the default or configured directory.'
    f'\n\n'
    rf'The default directory is: "~\.natlink", with "~" being your HOME directory: "{home}".'
    f'\tSo: "{home}\\.natlink"'
    f"\n"
    f'\nThere is also a custom way to configure the directory of your "natlink.ini" file:'
    f'\n'
    f'\nSpecify the environment variable "NATLINK_SETTINGSDIR", which should point to an existing directory.'
    f'\nthat ends with ".natlink".'
    f'\n'
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
    if isdir(natlink_settings_path):
        if natlink_settingsdir == natlink_settings_path:
            print(f'You specified for NATLINK_SETTINGSDIR: "{natlink_settingsdir}"')
        else:
            print(f'You specified for NATLINK_SETTINGSDIR: "{natlink_settingsdir}", which expands to: "{natlink_settings_path}".')
    else:
        print(f'You specified for NATLINK_SETTINGSDIR: "{natlink_settingsdir}"')
        print('This directory should exist! Please create manually or run the config program ')
else:
    print('The default config directory NATLINK_SETTINGSDIR should hold a valid config file "natlink.ini"')

msg = '\n'.join(['',
'Please try to run the config program (Command Line Interface) by running',
'***"Configure Natlink via GUI"*** or ***"Configure Natlink via CLI"***',
'\tfrom the Windows command prompt.',
'',
'After all these steps, (re)start Dragon and good luck...', '', ''])

print(msg)
