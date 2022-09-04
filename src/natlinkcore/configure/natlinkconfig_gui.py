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

SYMBOL_UP =    '▲'
SYMBOL_DOWN =  '▼'

# Hidden Columns and Project State
dragonfly2, vocola2, unimacro, extras = False, False, False, False

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
dragonfly2_section = [[sg.Text('Dragonfly', text_color='black')],
                     [sg.T('Dragonfly user directory:', tooltip='The directory to dragonfly2 user scripts (UserDirectory can also be used)'), sg.Input(Status.getDragonflyUserDirectory(), key='Set_UserDir_Dragonfly2', enable_events=True, readonly=True), sg.FolderBrowse(), sg.B("Clear", key='Clear_UserDir_Dragonfly2', enable_events=True)]]

vocola2_section = [[sg.T('Vocola', text_color='black')],
                   [sg.T('Vocola user directory:', enable_events=True, tooltip='Enable/disable Vocola by setting/clearing Vocola User Directory'), sg.I(Status.getVocolaUserDirectory(), key='Set_UserDir_Vocola2', enable_events=True, readonly=True), sg.FolderBrowse(), sg.B("Clear", key='Clear_UserDir_Vocola2', enable_events=True)],
                   [sg.Checkbox('Enable: distinguish between languages for Vocola command files', Status.getVocolaTakesLanguages(), enable_events=True, key='Toggle_Vocola2_Lang')],
                   [sg.Checkbox('Enable: Unimacro actions in Vocola', Status.getVocolaTakesUnimacroActions(), enable_events=True, key='Toggle_Vocola2_Unimacro_Actions')]]

unimacro_section = [[sg.T('Unimacro', text_color='black')],
                    [sg.T('Unimacro user directory:', tooltip=r'Where the Unimacro user INI files are located, and several other directories (~ or %HOME% allowed)'), sg.I(Status.getUnimacroUserDirectory(), key='Set_UserDir_Unimacro', enable_events=True, readonly=True), sg.FolderBrowse(), sg.B("Clear", key='Clear_UserDir_Unimacro', enable_events=True)]]

extras_section = [[sg.T('Natlink Loglevel:'),  sg.Combo(default_value=Status.getLogging(), values=("Critical",  "Fatal",  "Error", "Warning", "Info" , "Debug"), key='Set_Logging_Natlink', enable_events=True, auto_size_text=True, readonly=True)],
                  [sg.T('Autohotkey exe dir:'), sg.I(Status.getAhkExeDir(), key='Set_Exe_Ahk', enable_events=True, readonly=True), sg.FolderBrowse(), sg.B("Clear", key='Clear_Exe_Ahk', enable_events=True)],
                  [sg.T('Autohotkey scripts dir:'), sg.I(Status.getAhkUserDir(), key='Set_ScriptsDir_Ahk', enable_events=True, readonly=True), sg.FolderBrowse(), sg.B("Clear", key='Clear_ScriptsDir_Ahk', enable_events=True)]]

#### Main UI Layout ####
layout = [[sg.T('Environment:', font='bold'), sg.T(f'Windows OS: {osVersion.major}, Build: {osVersion.build}'), sg.T(f'Python: {pyVersion}'), sg.T(f'Dragon Version: {Status.getDNSVersion()}')],
          #### Projects Checkbox ####
          [sg.T('Configure Projects:', font='bold'), sg.Checkbox('Dragonfly', enable_events=True, key='dragonfly2-checkbox'), sg.Checkbox('Vocola', enable_events=True, key='vocola2-checkbox'), sg.Checkbox('Unimacro', enable_events=True, key='unimacro-checkbox')],
          #### Projects Hidden UI Columns - See above ####
          [collapse(dragonfly2_section, 'dragonfly2', dragonfly2)],
          [collapse(vocola2_section, 'vocola2', vocola2)],
          [collapse(unimacro_section, 'unimacro', unimacro)],
          [collapse(extras_section, 'extras', extras)],
          [sg.T(SYMBOL_DOWN, enable_events=True, k='extras-symbol-open', text_color='black'), sg.T('Extras', enable_events=True, text_color='black', k='extras-open')],
          #### Buttons at bottom ####
          [sg.Button('Exit')]]

window = sg.Window('Natlink configuration GUI', layout)

##### Config Functions #####
# Natlink
def SetNatlinkLoggingOutput(values, event):
    Config.setLogging(values['Set_Logging_Natlink'])

# Dragonfly2
def Dragonfly2UserDir(values, event):
    if event.startswith('Set'):
        # Threaded with pysimplegui perform_long_operation to prevent GUI from freezing while configuring/pip install Dragonfly
        window.perform_long_operation(lambda : Config.enable_dragonfly(values['Set_UserDir_Dragonfly2']), 'Thread_Done_Dragonfly')
    if event.startswith('Clear'):
        Config.disable_dragonfly()
        window['Set_UserDir_Dragonfly2'].update("")

# Vocola2
def Vocola2UserDir(values, event):
    if event.startswith('Set'):
    # Threaded with pysimplegui perform_long_operation to prevent GUI from freezing while configuring/pip install Vocola
        window.perform_long_operation(lambda : Config.enable_vocola(values['Set_UserDir_Vocola2']), 'Thread_Done_Vocola2')
    if event.startswith('Clear'):
        Config.disable_vocola()
        window['Set_UserDir_Vocola2'].update("")

def Vocola2TakesLanguages(values, event):
    if values['Toggle_Vocola2_Lang']:
        Config.enableVocolaTakesLanguages()
    else:
        Config.disableVocolaTakesLanguages()


def Vocola2UnimacroActions(values, event):
    if values['Toggle_Vocola2_Unimacro_Actions']:
        Config.enableVocolaTakesUnimacroActions()
    else:
        Config.disableVocolaTakesUnimacroActions()

# Unimacro
def UnimacroUserDir(values, event):
    if event.startswith('Set'):
    # Threaded with pysimplegui perform_long_operation to prevent GUI from freezing while configuring/pip install Unimacro 
        window.perform_long_operation(lambda : Config.enable_unimacro(values['Set_UserDir_Unimacro']), 'Thread_Done_Unimacro')
    if event.startswith('Clear'):
        Config.disable_unimacro()
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
natlink_dispatch = {'Set_Logging_Natlink': SetNatlinkLoggingOutput}
dragonfly2_dispatch = {'Set_UserDir_Dragonfly2': Dragonfly2UserDir, 'Clear_UserDir_Dragonfly2': Dragonfly2UserDir}
vocola2_dispatch = {'Set_UserDir_Vocola2': Vocola2UserDir, 'Clear_UserDir_Vocola2': Vocola2UserDir,'Toggle_Vocola2_Lang': Vocola2TakesLanguages,'Toggle_Vocola2_Unimacro_Actions': Vocola2UnimacroActions}
unimacro_dispatch = {'Set_UserDir_Unimacro': UnimacroUserDir, 'Clear_UserDir_Unimacro': UnimacroUserDir}
autohotkey_dispatch = {'Set_Exe_Ahk': AhkExeDir, 'Clear_Exe_Ahk': AhkExeDir, 'Set_ScriptsDir_Ahk': AhkUserDir,'Clear_ScriptsDir_Ahk': AhkUserDir}

#### Event Loop ####
try:
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        # Hidden Columns logic
        # TODO: if project is enabled, update the project state to enabled.
        elif event.startswith('dragonfly2'):
            dragonfly2 = not dragonfly2
            window['dragonfly2-checkbox'].update(dragonfly2)
            window['dragonfly2'].update(visible=dragonfly2)

        if event.startswith('vocola2'):
            vocola2 = not vocola2
            window['vocola2-checkbox'].update(vocola2)
            window['vocola2'].update(visible=vocola2)

        if event.startswith('unimacro'):
            unimacro = not unimacro
            window['unimacro-checkbox'].update(unimacro)
            window['unimacro'].update(visible=unimacro)

        if event.startswith('extras'):
            extras = not extras
            window['extras-symbol-open'].update(SYMBOL_DOWN if extras else SYMBOL_UP)
            window['extras'].update(visible=extras)

        # Dispatch events to call appropriate config function.
        if event in natlink_dispatch:
            func_to_call = natlink_dispatch[event]
            func_to_call(values, event)
        if event in dragonfly2_dispatch:
            func_to_call = dragonfly2_dispatch[event] # get function from dispatch dictionary (dragonfly2_dispatch)
            func_to_call(values, event) # event is passed to function for event specific handling. Set\Clear
        if event in vocola2_dispatch:
            func_to_call = vocola2_dispatch[event]
            func_to_call(values, event)
        if event in unimacro_dispatch:
            func_to_call = unimacro_dispatch[event]
            func_to_call(values, event)
        if event in autohotkey_dispatch:
            func_to_call = autohotkey_dispatch[event]
            func_to_call(values, event)
        Config.status.refresh()

except Exception as e:
    sg.Print('Exception in GUI event loop:', sg.__file__, e, keep_on_top=True, wait=True)

window.close()
