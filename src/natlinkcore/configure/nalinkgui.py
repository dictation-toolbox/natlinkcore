import sys
import platform

import PySimpleGUI as sg
# https://www.pysimplegui.org/en/latest/
from natlinkcore.configure.natlinkconfigfunctions import NatlinkConfig
from natlinkcore import natlinkstatus

pyVersion = platform.python_version()
osVersion = sys.getwindowsversion()

# Inlize the NatlinkConfig
Config = NatlinkConfig()
Status = natlinkstatus.NatlinkStatus()

# Hidden Columns and Project State
# TODO: if project is enabled, update the project state to enabled.
    # use enabled_packages for vocola, unimacro and dragonfly getDragonflyUserDirectory(), autohotkey Status.getAhkUserDir()?
dragonfly, vocola, unimacro, autohotkey = False, False, False, False


def collapse(layout, key, visible):
    """
    Helper function that creates a Column that can be later made hidden, thus appearing "collapsed"
    :param layout: The layout for the section
    :param key: Key used to make this seciton visible / invisible
    :param visible: bool visible / invisible
    :return: A pinned column that can be placed directly into your layout
    :rtype: sg.pin
    """
    return sg.pin(sg.Column(layout, key=key, visible=visible))

#### Hidden UI Columns ####
# FIXME: Any text sg.Input/sg.I with enable_events=True will fire the event with every keystroke. 
    # This is a problem when editing the a path in the input field.
# TODO: Status.getDragonflyUserDirectory() not implemented yet
dragonfly_section = [[sg.Text('Dragonfly', text_color='black')],
                     [sg.T('Dragonfly User Directory:', tooltip='The directory to Dragonfly user scripts (UserDirectory can also be used)'), sg.Input(key='Set_UserDir_Dragonfly', enable_events=True), sg.FolderBrowse(), sg.B("Clear", key='Clear_UserDir_Dragonfly', enable_events=True)]]

vocola2_section = [[sg.T('Vocola2', text_color='black')],
                   [sg.T('Vocola2 User Directory:', enable_events=True, tooltip='enable/disable Vocola by setting/clearing VocolaUserDirectory'), sg.I(Status.getVocolaUserDirectory(), key='Set_UserDir_Vocola', enable_events=True), sg.FolderBrowse(), sg.B("Clear", key='Clear_UserDir_Vocola', enable_events=True)],
                   [sg.Checkbox('Enable: Distinguish between languages for Vocola user files', Status.getVocolaTakesLanguages(), enable_events=True, key='Vocola_Lang')],
                   [sg.Checkbox('Enable: Unimacro actions in Vocola', Status.getVocolaTakesUnimacroActions(), enable_events=True, key='Vocola_Unimacro_Actions')]]

unimacro_section = [[sg.T('Unimacro', text_color='black')],
                    [sg.T('Unimacro User Directory:', tooltip=r'Where the Unimacro user INI files are located, and several other directories (~ or %HOME% allowed)'), sg.I(Status.getUnimacroUserDirectory(), key='Set_UserDir_Unimacro', enable_events=True), sg.FolderBrowse(), sg.B("Clear", key='Clear_UserDir_Unimacro', enable_events=True)]]

autohotkey_section = [[sg.T('Autohotkey', text_color='black')],
                      [sg.T('Autohotkey Exe:'), sg.I(Status.getAhkExeDir(), key='Set_Exe_Ahk', enable_events=True), sg.FileBrowse(file_types=("Executable ", "*.exe")), sg.B("Clear", key='Clear_Exe_Ahk', enable_events=True)],
                      [sg.T('Autohotkey Scripts Dir:'), sg.I(Status.getAhkUserDir(), key='Set_ScriptsDir_Ahk', enable_events=True), sg.FolderBrowse(), sg.B("Clear", key='Clear_ScriptsDir_Ahk', enable_events=True)]]

#### Main UI Layout ####
layout = [[sg.T('Environment:', font='bold'), sg.T(f'Windows OS: {osVersion.major}, Build: {osVersion.build}'), sg.T(f'Python: {pyVersion}'), sg.T(f'Dragon Version: {Status.getDNSVersion()}')],
          #### Nalink ####
          # TODO: Status.getUserDirectory() can not handle None for path
          [sg.T('Nalink:', font='bold'), sg.Checkbox('Enable Debug', key='Set_Debug_Natlink', enable_events=True)],
          [sg.I(key='Set_UserDir_Natlink',  tooltip=r'The directory where User Natlink grammar files are located (e.g., "~\UserDirectory")', enable_events=True), sg.FolderBrowse(), sg.B("Clear", key='Clear_UserDir_Natlink', enable_events=True)],
          #### Projects Checkbox ####
          [sg.T('Configure Projects:', font='bold')],
          [sg.Checkbox('Dragonfly', enable_events=True, key='dragonfly-checkbox'), sg.Checkbox('Vocola', enable_events=True, key='vocola2-checkbox'), sg.Checkbox('Unimacro', enable_events=True, key='unimacro-checkbox'), sg.Checkbox('AutoHotkey', key='autohotkey-checkbox', enable_events=True)],
          #### Projects Hidden  See Hidden UI Columns above ####
          [collapse(dragonfly_section, 'dragonfly', dragonfly)],
          [collapse(vocola2_section, 'vocola2', vocola)],
          [collapse(unimacro_section, 'unimacro', unimacro)],
          [collapse(autohotkey_section, 'autohotkey', autohotkey)],
          #### Buttons at bottom ####
          [sg.Button('Exit')]]

window = sg.Window('Natlink GUI', layout)

##### Config Functions #####
# Natlink
def SetNatlinkLoggingOutput(values, event):
    #TODO: Handle other logging levels
    if values['Set_Debug_Natlink']:
        Config.enableDebugOutput()
    else:
        Config.disableDebugOutput()


def NatlinkUserDir(values, event):
    if event.startswith('Set'):
        # Get the value from the input field with key 'Set_UserDir_Natlink' and set it as the UserDirectory
        Config.setDirectory('UserDirectory', values['Set_UserDir_Natlink']) 
    if event.startswith('Clear'):
        Config.clearDirectory('UserDirectory') # NatlinkCore Function to clear the directory
        window['Set_UserDir_Natlink'].update("") # Clear the input box with 'Set_UserDir_Natlink' key in GUI

# Dragonfly
def DragonflyUserDir(values, event):
    if event.startswith('Set'):
        Config.setDirectory('DragonflyUserDirectory', values['Set_UserDir_Dragonfly'])
    if event.startswith('Clear'):
        Config.clearDirectory('DragonflyUserDirectory')
        window['Set_UserDir_Dragonfly'].update("")

# Vocola
# TODO: Handle Vocola package not installed
def VocolaUserDir(valuesm, event):
    if event.startswith('Set'):
        Config.setDirectory('VocolaUserDirectory', values['Set_UserDir_Vocola'], section='vocola')
    if event.startswith('Clear'):
        Config.clearDirectory('VocolaUserDirectory', section='vocola')
        window['Set_UserDir_Vocola'].update("")

def VocolaTakesLanguages(values, event):
    if values['Vocola_Lang']:
        Config.enableVocolaTakesLanguages()
    else:
        Config.disableVocolaTakesLanguages()


def VocolaUnimacroActions(values, event):
    if values['Vocola_Unimacro_Actions']:
        Config.enableVocolaTakesUnimacroActions()
    else:
        Config.disableVocolaTakesUnimacroActions()

# Unimacro
def UnimacroUserDir(values, event):
    # TODO: Handle Unimacro package not installed
    if event.startswith('Set'):
        Config.setDirectory('UnimacroUserDirectory',
                            values['Set_UserDir_Unimacro'], section='unimacro')
        Config.setDirectory('UnimacroGrammarsDirectory', Config.status.getUnimacroGrammarsDirectory())
        Config.setDirectory('unimacro', 'unimacro')
    if event.startswith('Clear'):
        Config.clearDirectory('UnimacroUserDirectory', section='unimacro')
        Config.clearDirectory('UnimacroGrammarsDirectory')
        Config.clearDirectory('unimacro')
        window['Set_UserDir_Unimacro'].update("")

# Autohotkey
def AhkExeDir(values, event):
    if event.startswith('Set'):
        Config.setAhkExeDir(values['Set_Exe_Ahk'])
    if event.startswith('Clear'):
        Config.clearAhkExeDir()
        window['Set_Exe_Ahk'].update("")


def AhkUserDir(values, event):
    if event.startswith('Set'):
        Config.setAhkUserDir(values['Set_ScriptsDir_Ahk'])
    if event.startswith('Clear'):
        Config.clearAhkUserDir()
        window['Set_ScriptsDir_Ahk'].update("")


# Lookup dictionary that maps keys as events to a function to call in Event Loop.
nalink_dispatch = {'Set_Debug_Natlink': SetNatlinkLoggingOutput, 'Set_UserDir_Natlink': NatlinkUserDir, 'Clear_UserDir_Natlink': NatlinkUserDir}
dragonfly_dispatch = {'Set_UserDir_Dragonfly': DragonflyUserDir, 'Clear_UserDir_Dragonfly': DragonflyUserDir}
vocola_dispatch = {'Set_UserDir_Vocola': VocolaUserDir, 'Clear_UserDir_Vocola': VocolaUserDir,'Vocola_Lang': VocolaTakesLanguages,'Vocola_Unimacro_Actions': VocolaUnimacroActions}  # , 'Set_GrammarsDir_Vocola': VocolaGrammarsDir
unimacro_dispatch = {'Set_UserDir_Unimacro': UnimacroUserDir, 'Clear_UserDir_Unimacro': UnimacroUserDir}
autohotkey_dispatch = {'Set_Exe_Ahk': AhkExeDir, 'Clear_Exe_Ahk': AhkExeDir, 'Set_ScriptsDir_Ahk': AhkUserDir,'Clear_ScriptsDir_Ahk': AhkUserDir}

#### Event Loop ####
try:
    while True:
        event, values = window.read()
       # print(event, values)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        # Hidden Columns logic
        # TODO: if project is enabled, then show the column
        elif event.startswith('dragonfly'):
            dragonfly = not dragonfly
            window['dragonfly-checkbox'].update(dragonfly)
            window['dragonfly'].update(visible=dragonfly)

        if event.startswith('vocola2'):
            vocola = not vocola
            window['vocola2-checkbox'].update(vocola)
            window['vocola2'].update(visible=vocola)

        if event.startswith('unimacro'):
            unimacro = not unimacro
            window['unimacro-checkbox'].update(unimacro)
            window['unimacro'].update(visible=unimacro)

        if event.startswith('autohotkey'):
            autohotkey = not autohotkey
            window['autohotkey-checkbox'].update(autohotkey)
            window['autohotkey'].update(visible=autohotkey)

        # Dispatch events to call appropriate config function.
        if event in nalink_dispatch:
            func_to_call = nalink_dispatch[event] # get function from dispatch dictionary (nalink_dispatch)
            func_to_call(values, event) # event is passed to function for event specific handling. Set\Clear
        if event in dragonfly_dispatch:
            func_to_call = dragonfly_dispatch[event]
            func_to_call(values, event)
        if event in vocola_dispatch:
            func_to_call = vocola_dispatch[event]
            func_to_call(values, event)
        if event in unimacro_dispatch:
            func_to_call = unimacro_dispatch[event]
            func_to_call(values, event)
        if event in autohotkey_dispatch:
            func_to_call = autohotkey_dispatch[event]
            func_to_call(values, event)
        Config.status.refresh()

except Exception as e:
    sg.Print('Exception in GUI event loop:',
             sg.__file__, e, keep_on_top=True, wait=True)

window.close()
