#pylint:disable=W0621, W0703
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
dragonfly2_state, unimacro_state, extras_state = Status.dragonflyIsEnabled(), Status.unimacroIsEnabled(), False

# Threaded perform_long_operation state
Thread_Running = False

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

unimacro_section = [[sg.T('Unimacro', text_color='black')],
                    [sg.T('Unimacro user directory:', tooltip=r'Where the Unimacro user INI files are located, and several other directories (~ or %HOME% allowed)'), sg.I(Status.getUnimacroUserDirectory(), key='Set_UserDir_Unimacro', enable_events=True, readonly=True), sg.FolderBrowse(), sg.B("Clear", key='Clear_UserDir_Unimacro', enable_events=True)]]

extras_section = [[sg.T('Natlink Loglevel:'),  sg.Combo(default_value=Status.getLogging(), values=("Critical",  "Fatal",  "Error", "Warning", "Info" , "Debug"), key='Set_Logging_Natlink', enable_events=True, auto_size_text=True, readonly=True)],
                  [sg.T('Autohotkey exe dir:'), sg.I(Status.getAhkExeDir(), key='Set_Exe_Ahk', enable_events=True, readonly=True), sg.FolderBrowse(), sg.B("Clear", key='Clear_Exe_Ahk', enable_events=True)],
                  [sg.T('Autohotkey scripts dir:'), sg.I(Status.getAhkUserDir(), key='Set_ScriptsDir_Ahk', enable_events=True, readonly=True), sg.FolderBrowse(), sg.B("Clear", key='Clear_ScriptsDir_Ahk', enable_events=True)],
                  [sg.T('Natlink GUI Output')],
                  [sg.Output(size=(40,10), echo_stdout_stderr=True, expand_x=True, key='-OUTPUT-')]]

#### Main UI Layout ####
layout = [[sg.T('Environment:', font='bold'), sg.T(f'Windows OS: {osVersion.major}, Build: {osVersion.build}'), sg.T(f'Python: {pyVersion}'), sg.T(f'Dragon Version: {Status.getDNSVersion()}')],
          #### Projects Checkbox ####
          [sg.T('Configure Projects:', font='bold'), sg.Checkbox('Dragonfly', enable_events=True, key='dragonfly2-checkbox', default=dragonfly2_state), sg.Checkbox('Unimacro', enable_events=True, key='unimacro-checkbox', default=unimacro_state)],
          #### Projects Hidden UI Columns - See above ####
          [collapse(dragonfly2_section, 'dragonfly2', dragonfly2_state)],
          [collapse(unimacro_section, 'unimacro', unimacro_state)],
          [sg.T(SYMBOL_DOWN, enable_events=True, k='extras-symbol-open', text_color='black'), sg.T('Natlink Extras', enable_events=True, text_color='black', k='extras-open')],
          [collapse(extras_section, 'extras', extras_state)],
          #### Buttons at bottom ####
          [sg.Button('Exit'), sg.B('Open Natlink Config File', key='Open_Config', enable_events=True, auto_size_button=True)]]

window = sg.Window('Natlink configuration GUI', layout, enable_close_attempted_event=True)

def ThreadIsRunning():
    global Thread_Running
    Thread_Running = not Thread_Running      

##### Config Functions #####
# Natlink
def SetNatlinkLoggingOutput(values, event):
    Config.setLogging(values['Set_Logging_Natlink'])

# Dragonfly2
def Dragonfly2UserDir(values, event):
    if event.startswith('Set') and not ThreadIsRunning():
        # Threaded with pysimplegui perform_long_operation to prevent GUI from freezing while configuring/pip install Dragonfly
        window.perform_long_operation(lambda: Config.enable_dragonfly(values['Set_UserDir_Dragonfly2']), 'Thread_Done_Dragonfly')
    if event.startswith('Clear'):
        Config.disable_dragonfly()
        window['Set_UserDir_Dragonfly2'].update("")

# Unimacro
def UnimacroUserDir(values, event):
    if event.startswith('Set') and not ThreadIsRunning():
        window.perform_long_operation(lambda: Config.enable_unimacro(values['Set_UserDir_Unimacro']), 'Thread_Done_Unimacro')
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

def OpenNatlinkConfig(values, event):
    Config.openConfigFile()

# Lookup dictionary that maps keys as events to a function to call in Event Loop.
natlink_dispatch = {'Set_Logging_Natlink': SetNatlinkLoggingOutput, 'Open_Config': OpenNatlinkConfig}
dragonfly2_dispatch = {'Set_UserDir_Dragonfly2': Dragonfly2UserDir, 'Clear_UserDir_Dragonfly2': Dragonfly2UserDir}
unimacro_dispatch = {'Set_UserDir_Unimacro': UnimacroUserDir, 'Clear_UserDir_Unimacro': UnimacroUserDir}
autohotkey_dispatch = {'Set_Exe_Ahk': AhkExeDir, 'Clear_Exe_Ahk': AhkExeDir, 'Set_ScriptsDir_Ahk': AhkUserDir,'Clear_ScriptsDir_Ahk': AhkUserDir}

#### Event Loop ####
try:
    while True:
        event, values = window.read()
        if (event == '-WINDOW CLOSE ATTEMPTED-' or event == 'Exit') and not Thread_Running:
            break
        # Hidden Columns logic
        # TODO: if project is enabled, update the project state to enabled.
        if event.startswith('dragonfly2'):
            dragonfly2_state = not dragonfly2_state
            window['dragonfly2-checkbox'].update(dragonfly2_state)
            window['dragonfly2'].update(visible=dragonfly2_state)

        elif event.startswith('unimacro'):
            unimacro_state = not unimacro_state
            window['unimacro-checkbox'].update(unimacro_state)
            window['unimacro'].update(visible=unimacro_state)

        elif event.startswith('extras'):
            window['extras-symbol-open'].update(SYMBOL_DOWN if extras_state else SYMBOL_UP)
            extras_state = not extras_state
            window['extras'].update(visible=extras_state)
        
        # Wait for threaded perform_long_operation to complete 
        elif event.startswith('Thread_Done'):
            Thread_Running = not Thread_Running

        elif Thread_Running:
            choice = sg.popup(f'Please Wait: Pip install is in progress', keep_on_top=True, custom_text=('Wait','Force Close'))
            if choice == 'Force Close':
                break

        # Dispatch events to call appropriate config function.
        elif event in natlink_dispatch:
            func_to_call = natlink_dispatch[event]
            func_to_call(values, event)
        elif event in dragonfly2_dispatch:
            func_to_call = dragonfly2_dispatch[event] # get function from dispatch dictionary (dragonfly2_dispatch)
            func_to_call(values, event) # event is passed to function for event specelific handling. Set\Clear
        elif event in unimacro_dispatch:
            func_to_call = unimacro_dispatch[event]
            func_to_call(values, event)
        elif event in autohotkey_dispatch:
            func_to_call = autohotkey_dispatch[event]
            func_to_call(values, event)

except Exception as e:
    sg.Print('Exception in GUI event loop:', sg.__file__, e, keep_on_top=True, wait=True)
finally:
    Config.status.refresh()

window.close()
