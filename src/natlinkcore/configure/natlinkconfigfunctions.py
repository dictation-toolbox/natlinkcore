#
# natlinkconfigfunctions.py

#   This module performs the configuration functions.
#   called from nalinkgui (a PySimpleGUI window)),
#   or CLI, see below
#
#   Quintijn Hoogenboom, January 2008 (...), August 2022
#

#pylint:disable=C0302, W0702, R0904, C0116, W0613, R0914, R0912, R1732, W1514, W0107, W1203
"""With the functions in this module Natlink can be configured.

These functions are called in different ways:
-Through the natlinkconfig program (GUI)
-Via the natlinkconfig_cli.py (command line interface)
-By running natlinkconfig_cli in batch mode.
"""
import os
import shutil
import sys
import subprocess
from pprint import pformat
from pathlib import Path
import configparser
import logging

try:
    from natlinkcore import natlinkstatus
except OSError:
    print('error when starting natlinkconfigfunctions')
from natlinkcore import config
from natlinkcore import loader
from natlinkcore import readwritefile
from natlinkcore import tkinter_dialogs

isfile, isdir, join = os.path.isfile, os.path.isdir, os.path.join


def do_pip(*args):
    """
    Run a pip command with args. 
    Diagnostic logging.3
    """
 

    command = [sys.executable,"-m", "pip"] + list(args)
    logging.info(f"command:  {command} ")
    completed_process=subprocess.run(command,capture_output=True)
    logging.debug(f"completed_process:  {completed_process}")
    completed_process.check_returncode()

class NatlinkConfig:
    """performs the configuration tasks of Natlink
    
    setting UserDirectory, UnimacroDirectory and options, VocolaDirectory and options,
    DragonflyDirectory, Autohotkey options (ahk), and Debug option of Natlink.
    and also clearing the different directories.

    Changes are written in the config file, from which the path is taken from the loader instance.
    """
    def __init__(self,extra_pip_options=None):
        self.extra_pip_options = [] if extra_pip_options is None else extra_pip_options

        self.config_path = self.get_check_config_locations()
        self.config_dir = str(Path(self.config_path).parent)
        self.status = natlinkstatus.NatlinkStatus()
        self.Config = self.getConfig()  # get the config instance of config.NatlinkConfig
        self.check_config()
        # for convenience in other places:
        self.home_path = str(Path.home())
        self.documents_path = str(Path.home()/'Documents')
        self.natlinkconfig_path = config.expand_natlink_settingsdir()
        pass
    
    def get_check_config_locations(self):
        
        """check the location/locations as given by the loader
        """
        config_path, fallback_path = loader.config_locations()  
        
        if not isfile(config_path):
            config_dir = Path(config_path).parent
            if not config_dir.is_dir():
                config_dir.mkdir(parents=True)
            shutil.copyfile(fallback_path, config_path)
        return config_path

    def check_config(self):
        """check config_file for possibly unwanted settings
        """
        # ensure the [directories] section is present:
        try:
            sect = self.Config['directories']
        except KeyError:
            self.Config.add_section('directories')
            self.config_write()


        self.config_remove(section='directories', option='default_config')
        
        # check for default options missing:
        # ret = config.NatlinkConfig.get_default_config()
        # for ret_sect in ret.sections():
        #     if self.Config.has_section(ret_sect):
        #         continue
        #     for ret_opt in self.Config[section].keys():
        #         ret_value = ret[ret_sect][ret_opt]
        #         print(f'fix default section/key: "ret_sect", "ret_opt" to "ret_value"')
        
        # change default unimacrogrammarsdirectory:
        section = 'directories'
        option = 'unimacrogrammarsdirectory'
        old_prefix = 'natlink_user'
        new_prefix = 'unimacro'
        try:
            value = self.Config[section][option]
            if value and value.find('natlink_user') == 0:
                value = value.replace(old_prefix,new_prefix)
                self.config_set(section, option, value)
                logging.info(f'changed in "natlink.ini", section "directories", unimacro setting "{option}" to value: "{value}"')
                pass
        except KeyError:
            pass
        
        if loader.had_msg_error:
            logging.error('The environment variable "NATLINK_USERDIR" has been changed to "NATLINK_SETTINGSDIR" by the user, but has a conclicting value')
            logging.error('Please remove "NATLINK_USERDIR", in the windows "environment variables", dialog User variables, and restart your program')

        if loader.had_msg_warning:
            logging.error('The key of the environment variable "NATLINK_USERDIR" should be changed to "NATLINK_SETTINGSDIR".')
            logging.error('You can do so in windows "environment variables", dialog "User variables".')
            
            
        # for key, value in self.Config[section].items():
        #     print(f'key: {key}, value: {value}')

    def getConfig(self):
        """return the config instance
        """
        rwfile = readwritefile.ReadWriteFile()
        config_text = rwfile.readAnything(self.config_path)
        _config = configparser.ConfigParser()
        _config.read_string(config_text)
        self.config_encoding = rwfile.encoding
        return _config

    def config_get(self, section, option):
        """set a setting into the natlink ini file

        """
        try:
            return self.Config.get(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return None
 
    def config_set(self, section, option, value):
        """set a setting into an inifile (possibly other than natlink.ini)
    
        Set the setting in self.Config.
        
        Then write with the setting included to config_path with config_encoding.
        When this encoding is ascii, but there are (new) non-ascii characters,
        the file is written as 'utf-8'.

        """
        if not value:
            return self.config_remove(section, option)
        
        if not self.Config.has_section(section):
            self.Config.add_section(section)
            
        value = str(value)
        self.Config.set(section, option, str(value))
        self.config_write()
        self.status = natlinkstatus.NatlinkStatus()
        return True
    
    def config_write(self):
        """write the (changed) content to the ini (config) file
        """
        try:
            with open(self.config_path, 'w', encoding=self.config_encoding) as fp:
                self.Config.write(fp)   
        except UnicodeEncodeError as exc:
            if self.config_encoding != 'ascii':
                print(f'UnicodeEncodeError, cannot encode with encoding "{self.config_encoding}" the config data to file "{self.config_path}"')
                raise UnicodeEncodeError from exc
            with open(self.config_path, 'w', encoding='utf-8') as fp:
                self.Config.write(fp)   

    def config_remove(self, section, option):
        """removes from config file
        
        same effect as setting an empty value
        """
        if not self.Config.has_section(section):
            return
        self.Config.remove_option(section, option)
        if not self.Config.options(section):
            if section not in ['directories', 'settings', 'userenglish-directories', 'userspanish-directories']:
                self.Config.remove_section(section)
        self.config_write()
        self.status = natlinkstatus.NatlinkStatus()

    # def setUserDirectory(self, arg):
    #     self.setDirectory('UserDirectory', arg)
    # def clearUserDirectory(self, arg):
    #     self.clearDirectory('UserDirectory')
        

    def setDirectory(self, option, dir_path, section=None):
        """set the directory, specified with "key", to dir_path
        """
        section = section or 'directories'
        if not dir_path:
            logging.info('==== Please specify the wanted directory in Dialog window ====\n')
            prev_path = self.config_get('previous settings', option) or self.documents_path
            dir_path = tkinter_dialogs.GetDirFromDialog(title=f'Please choose a "{option}"', initialdir=prev_path)
            if not dir_path:
                print('No valid directory specified')
                return

        dir_path = dir_path.strip()
        directory = createIfNotThere(dir_path, level_up=1)
        if not (directory and Path(directory).is_dir()):
            if directory is False:
                directory = config.expand_path(dir_path)
            if dir_path == directory:
                logging.info(f'Cannot set "{option}", the given path is invalid: "{directory}"')
            else:
                logging.info(f'Cannot set "{option}", the given path is invalid: "{directory}" ("{dir_path}")')
            return
        
        nice_dir_path = self.prefix_home(dir_path)
        nice_dir_path = nice_dir_path.replace('/', '\\')        
        self.config_set(section, option, nice_dir_path)
        self.config_remove('previous settings', option)
        if section == 'directories':
            logging.info(f'Set option "{option}" to "{dir_path}"')
        else:
            logging.info(f'Set in section "{section}", option "{option}" to "{dir_path}"')
        return
        
    def clearDirectory(self, option, section=None):
        """clear the setting of the directory designated by option
        """
        section = section or 'directories'
        old_value = self.config_get(section, option)
        if not old_value:
            logging.info(f'The "{option}" was not set, nothing changed...')
            return
        if isValidDir(old_value):
            self.config_set('previous settings', option, old_value)
        else:
            self.config_remove('previous settings', option)
            
        self.config_remove(section, option)
        logging.info(f'cleared "{option}"')
 
 
    def prefix_home(self, dir_path):
        """if dir_path startswith home directory, replace this with "~"
        """
        home_path = str(Path.home())
        if dir_path.startswith(home_path):
            dir_path = dir_path.replace(home_path, "~")
        return dir_path
            
 
    def setFile(self, option, file_path, section):
        """set the file, specified with "key", to file_path
        """
        if not file_path:

            prev_path = self.config_get('previous settings', option) or ""
            file_path = tkinter_dialogs.GetFileFromDialog(title=f'Please choose a "{option}"', initialdir=prev_path)
            if not file_path:
                logging.info('No valid file specified')
                return
        file_path = file_path.strip()
        if not Path(file_path).is_file():
            logging.info(f'No valid file specified ("{file_path}")')
            
        self.config_set(section, option, file_path)
        self.config_remove('previous settings', option)
        logging.info(f'Set in section "{section}", option "{option}" to "{file_path}"')
        return
        
    def clearFile(self, option, section):
        """clear the setting of the directory designated by option
        """
        old_value = self.config_get(section, option)
        if not old_value:
            logging.info(f'The "{option}" was not set, nothing changed...')
            return
        if isValidFile(old_value):
            self.config_set('previous settings', option, old_value)
        else:
            self.config_remove('previous settings', option)
            
        self.config_remove(section, option)
        logging.info(f'cleared "{option}"')
  

    def setLogging(self, logginglevel):
        """Sets the natlink logging output
        logginglevel (str) -- Critical, Fatal, Error, Warning, Info, Debug
        """
        # Config.py handles log level str upper formatting from ini
        value = logginglevel.title()
        old_value = self.config_get('settings', "log_level")
        if old_value == value:
            logging.info(f'setLogging, setting is already "{old_value}"')
            return True
        if value in ["Critical", "Fatal", "Error", "Warning", "Info", "Debug"]:
            logging.info(f'setLogging, setting logging to: "{value}"')
            self.config_set('settings', "log_level", value)
            if old_value is not None:
                self.config_set('previous settings', "log_level", old_value)
            return True
        return False

    def disableDebugOutput(self):
        """disables the Natlink debug output
        """
        key = 'log_level'
        # section = 'settings'
        old_value = self.config_get('previous settings', key)
        if old_value:
            self.config_set('settings', key, old_value)
        self.config_set('settings', key, 'INFO')

    def enable_unimacro(self, arg):
        unimacro_user_dir = self.status.getUnimacroUserDirectory()
        if unimacro_user_dir and isdir(unimacro_user_dir):
            logging.info(f'UnimacroUserDirectory is already defined: "{unimacro_user_dir}"\n\tto change, first clear (option "O") and then set again')
            logging.info('\nWhen you want to upgrade Unimacro, also first clear ("O"), then choose this option ("o") again.\n')
            return

        uni_dir = self.status.getUnimacroDirectory()
        if uni_dir:
            logging.info('==== instal and/or update unimacro====\n')            
            try:
                do_pip("install", *self.extra_pip_options, "--upgrade", "unimacro")
            except subprocess.CalledProcessError:
                logging.info('====\ncould not pip install --upgrade unimacro\n====\n')
                return
        else:
            try:
                do_pip("install",*self.extra_pip_options, "unimacro")
            except subprocess.CalledProcessError:
                logging.info('====\ncould not pip install unimacro\n====\n')
                return
        self.status.refresh()   # refresh status
        uni_dir = self.status.getUnimacroDirectory()

        self.setDirectory('UnimacroUserDirectory', arg, section='unimacro')
        unimacro_user_dir = self.config_get('unimacro', 'unimacrouserdirectory')
        if not unimacro_user_dir:
            return
        uniGrammarsDir = r'unimacro\unimacrogrammars'
        self.setDirectory('unimacrodirectory','unimacro')  #always unimacro

        self.setDirectory('unimacrogrammarsdirectory', uniGrammarsDir)

    def disable_unimacro(self, arg=None):
        """disable unimacro, do not expect arg
        """
        self.clearDirectory('UnimacroUserDirectory', section='unimacro')
        self.config_remove('directories', 'unimacrogrammars')
        self.config_remove('directories', 'unimacrogrammarsdirectory')   # could still be there...
        self.config_remove('directories', 'unimacro')
        self.config_remove('directories', 'unimacrodirectory')  # could still be there...
        self.status.refresh()

    ### Dragonfly:

    def enable_dragonfly(self, arg):
        dragonfly_user_dir = self.status.getDragonflyUserDirectory()
        if dragonfly_user_dir and isdir(dragonfly_user_dir):
            logging.info(f'DragonflyUserDirectory is already defined: "{dragonfly_user_dir}"\n\tto change, first clear (option "D") and then set again')
            logging.info('\nWhen you want to upgrade Dragonfly, also first clear ("D"), then choose this option ("d") again.\n')
            return

        df_dir = self.status.getDragonflyDirectory()
        if df_dir:
            logging.info('==== instal and/or update dragonfly2====\n')            
            try:
                do_pip( "install", *self.extra_pip_options,"--upgrade", "dragonfly2")
            except subprocess.CalledProcessError:
                logging.info('====\ncould not pip install --upgrade dragonfly2\n====\n')
                return
        else:
            try:
                do_pip( "install", *self.extra_pip_options, "dragonfly2")
            except subprocess.CalledProcessError:
                logging.info('====\ncould not pip install dragonfly2\n====\n')
                return
        self.status.refresh()   # refresh status
        df_dir = self.status.getDragonflyDirectory()

        self.setDirectory('DragonflyUserDirectory', arg)
        dragonfly_user_dir = self.config_get('dragonfly', 'dragonflyuserdirectory')
        if not dragonfly_user_dir:
            return


    def disable_dragonfly(self, arg=None):
        """disable dragonfly, do not expect arg
        """
        self.config_remove('directories', 'dragonflyuserdirectory')  # could still be there...
        self.status.refresh()


    def enable_vocola(self, arg):
        """enable vocola, by setting arg (prompting if False), and other settings
        """
        vocola_user_dir = self.status.getVocolaUserDirectory()
        if vocola_user_dir and isdir(vocola_user_dir):
            logging.info(f'VocolaUserDirectory is already defined: "{vocola_user_dir}"\n\tto change, first clear (option "V") and then set again')
            logging.info('\nWhen you want to upgrade Vocola (vocola2), also first clear ("V"), then choose this option ("v") again.\n')
            return

        voc_dir = self.status.getVocolaDirectory()
        if voc_dir:
            logging.info('==== instal and/or update vocola2====\n')
            try:
                do_pip("install",*self.extra_pip_options, "--upgrade", "vocola2")
            except subprocess.CalledProcessError:
                logging.info('====\ncould not pip install --upgrade vocola2\n====\n')
                return
        else:
            try:
                do_pip("install",*self.extra_pip_options, "vocola2")
            except subprocess.CalledProcessError:
                logging.info('====\ncould not pip install vocola2\n====\n')
                return
        self.status.refresh()   # refresh status
        voc_dir = self.status.getVocolaDirectory()

        self.setDirectory('VocolaUserDirectory', arg, section='vocola')
        vocola_user_dir = self.config_get('vocola', 'VocolaUserDirectory')
        if not vocola_user_dir:
            return
        # vocGrammarsDir = self.status.getVocolaGrammarsDirectory()
        vocGrammarsDir = r'natlink_settings\vocolagrammars'
        self.setDirectory('vocoladirectory','vocola2')  #always vocola2
        self.setDirectory('vocolagrammarsdirectory', vocGrammarsDir)
        self.copyUnimacroIncludeFile()
        

    def disable_vocola(self, arg=None):
        """disable vocola, arg not needed/used
        """
        self.clearDirectory('VocolaUserDirectory', section='vocola')
        self.config_remove('directories', 'vocolagrammars')
        self.config_remove('directories', 'vocolagrammarsdirectory')   # could still be there
        self.config_remove('directories', 'vocola')
        self.config_remove('directories', 'vocoladirectory')   #could still be there...

    def copyUnimacroIncludeFile(self):
        """copy Unimacro include file into Vocola user directory

        """
        uscFile = 'Unimacro.vch'
        # also remove usc.vch from VocolaUserDirectory
        dtactionsDir = Path(self.status.getDtactionsDirectory())
        fromFolder = Path(dtactionsDir)/'Vocola_compatibility'
        toFolder = Path(self.status.getVocolaUserDirectory())
        if not dtactionsDir.is_dir():
            mess = f'copyUnimacroIncludeFile: dtactionsDir "{str(dtactionsDir)}" is not a directory'
            logging.warning(mess)
            return
        fromFile = fromFolder/uscFile
        if not fromFile.is_file():
            mess = f'copyUnimacroIncludeFile: file "{str(fromFile)}" does not exist (is not a valid file)'
            logging.warning(mess)
            return
        if not toFolder.is_dir():
            mess = f'copyUnimacroIncludeFile: vocolaUserDirectory does not exist "{str(toFolder)}" (is not a directory)'
            logging.warning(mess)
            return
        
        toFile = toFolder/uscFile
        if toFolder.is_file():
            logging.info(f'remove previous "{str(toFile)}"')
            try:
                os.remove(toFile)
            except:
                mess = f'copyUnimacroIncludeFile: Could not remove previous version of "{str(toFile)}"'
                logging.info(mess)
        try:
            shutil.copyfile(fromFile, toFile)
            logging.info(f'copied "{uscFile}" from "{str(fromFolder)}" to "{str(toFolder)}"')
        except:
            mess = f'Could not copy new version of "{uscFile}", from "{str(fromFolder)}" to "{str(toFolder)}"'
            logging.warning(mess)
            return
        return

    def removeUnimacroIncludeFile(self):
        """remove Unimacro include file from Vocola user directory

        """
        uscFile = 'Unimacro.vch'
        # also remove usc.vch from VocolaUserDirectory
        toFolder = Path(self.status.getVocolaUserDirectory())
        if not toFolder.is_dir():
            mess = f'removeUnimacroIncludeFile: vocolaUserDirectory does not exist "{str(toFolder)}" (is not a directory)'
            logging.warning(mess)
            return
        
        toFile = toFolder/uscFile
        if toFolder.is_file():
            logging.info(f'remove Unimacro include file "{str(toFile)}"')
            try:
                os.remove(toFile)
            except:
                mess = f'copyUnimacroIncludeFile: Could not remove previous version of "{str(toFile)}"'
                logging.warning(mess)

    def includeUnimacroVchLineInVocolaFiles(self, toFolder=None):
        """include the Unimacro wrapper support line into all Vocola command files
        
        as a side effect, set the variable for Unimacro in Vocola support:
        VocolaTakesUnimacroActions...
        """
        uscFile = 'Unimacro.vch'
        oldUscFile = 'usc.vch'
##        reInclude = re.compile(r'^include\s+.*unimacro.vch;$', re.MULTILINE)
##        reOldInclude = re.compile(r'^include\s+.*usc.vch;$', re.MULTILINE)

        # also remove includes of usc.vch
        vocUserDir = self.status.getVocolaUserDirectory()   
        toFolder = toFolder or vocUserDir
        subDirectory = toFolder != vocUserDir
        if subDirectory:
            includeLine = f'include ..\\{uscFile};\n'
            oldIncludeLines = [f'include {oldUscFile};',
                               f'include ..\\{oldUscFile};',
                               f'include {uscFile};'
                               ]
        else:
            includeLine = f'include {uscFile};\n'
            oldIncludeLines = [f'include {oldUscFile};',
                               f'include ..\\{oldUscFile};',
                               f'include ..\\{uscFile};'
                               ]
            
        if not os.path.isdir(toFolder):
            if subDirectory:
                mess = f'cannot find Vocola command files in sub directory, not a valid path: {toFolder}'
            else:
                mess = f'cannot find Vocola command files in irectory, not a valid path: {toFolder}'
            logging.warning(mess)
            return mess
        
        nFiles = 0
        for f in os.listdir(toFolder):
            if f.endswith(".vcl"):
                F = os.path.join(toFolder, f)
                changed = 0
                correct = 0
                Output = []
                for line in open(F, 'r'):
                    if line.strip().lower() == includeLine.strip().lower():
                        correct = 1
                    for oldLine in oldIncludeLines:
                        if line.strip().lower() == oldLine.lower():
                            changed += 1
                            break
                    else:
                        Output.append(line)
                if changed or not correct:
                    # print(f'{F}: wrong lines: {changed}, had correct line: {bool(correct)}')   # changes were made:
                    if not correct:
                        # print(f'\tinclude: "{includeLine.strip()}"')
                        Output.insert(0, includeLine)
                    open(F, 'w').write(''.join(Output))
                    nFiles += 1
            elif len(f) == 3:
                # subdirectory, recursive
                self.includeUnimacroVchLineInVocolaFiles(toFolder=os.path.join(toFolder, f))
        mess = f'changed {nFiles} files in {toFolder}'
        logging.warning(mess)
        return True

    def removeUnimacroVchLineInVocolaFiles(self, toFolder=None):
        """remove the Unimacro wrapper support line into all Vocola command files
        
        toFolder set with recursive calls...
        """
        uscFile = 'Unimacro.vch'
        oldUscFile = 'usc.vch'
##        reInclude = re.compile(r'^include\s+.*unimacro.vch;$', re.MULTILINE)
##        reOldInclude = re.compile(r'^include\s+.*usc.vch;$', re.MULTILINE)
        
        # also remove includes of usc.vch
        if toFolder:
            pass            # for recursive call language subfolders:
        else:
            toFolder = self.status.getVocolaUserDirectory()
            
        oldIncludeLines = [f'include {oldUscFile};',
                           f'include ..\\{oldUscFile};',
                           f'include {uscFile};',
                           f'include ..\\{uscFile};',
                           f'include ../{oldUscFile};',
                           f'include ../{uscFile};',
                           ]

            
        if not os.path.isdir(toFolder):
            mess = f'cannot find Vocola command files directory, not a valid path: {toFolder}'
            logging.warning(mess)
            return mess
        nFiles = 0
        for f in os.listdir(toFolder):
            F = os.path.join(toFolder, f)
            if f.endswith(".vcl"):
                changed = 0
                Output = []
                for line in open(F, 'r'):
                    for oldLine in oldIncludeLines:
                        if line.strip().lower() == oldLine.lower():
                            changed = 1
                            break
                    else:
                        Output.append(line)
                if changed:
                    # had break, so changes were made:
                    open(F, 'w').write(''.join(Output))
                    nFiles += 1
            elif len(f) == 3:
                self.removeUnimacroVchLineInVocolaFiles(toFolder=os.path.join(toFolder, f))
        # self.disableVocolaTakesUnimacroActions()
        mess = f'removed include lines from {nFiles} files in {toFolder}'
        logging.warning(mess)

        return True

    def enableVocolaTakesLanguages(self):
        """setting registry  so Vocola can divide different languages

        """
        key = "vocolatakeslanguages"
        self.config_set('vocola', key, 'True')
        

    def disableVocolaTakesLanguages(self):
        """disables so Vocola cannot take different languages
        """
        key = "vocolatakeslanguages"
        self.config_set('vocola', key, 'False')

    def enableVocolaTakesUnimacroActions(self):
        """do setting, so Vocola can take Unimacro Actions
        also include correct include line in each Vcl file
        and copy Unimacro.vch to the VocolaUserDirectory

        """
        key = "vocolatakesunimacroactions"
        self.config_set('vocola', key, 'True')
        self.includeUnimacroVchLineInVocolaFiles()
        self.copyUnimacroIncludeFile()

    def disableVocolaTakesUnimacroActions(self):
        """disables so Vocola does not take Unimacro Actions
        and remove Unimacro.vch and the include lines in each .vcl file
        """
        key = "vocolatakesunimacroactions"
        self.config_set('vocola', key, 'False')
        self.removeUnimacroVchLineInVocolaFiles()
        self.removeUnimacroIncludeFile()
        
    def openConfigFile(self):
        """open the natlink.ini config file
        """
        assert self.config_path and os.path.isfile(self.config_path)
        #     logging.warning(f'openConfigFile, no valid config_path specified: "{self.config_path}"')
        #     return False
        os.startfile(self.config_path)
        logging.info(f'opened "{self.config_path}" in a separate window')
        return True

    def setAhkExeDir(self, arg):
        """set ahkexedir to a valid folder
        """
        key = 'ahkexedir'
        self.setDirectory(key, arg, section='autohotkey')

    def clearAhkExeDir(self, arg=None):
        """set ahkexedir to a valid folder
        """
        key = 'ahkexedir'
        self.clearDirectory(key, section='autohotkey')

    def setAhkUserDir(self, arg):
        """set ahkuserdir to a valid folder
        """
        key = 'ahkuserdir'
        self.setDirectory(key, arg, section='autohotkey')

    def clearAhkUserDir(self, arg=None):
        """clear Autohotkey user directory
        """
        key = 'ahkuserdir'
        self.clearDirectory(key, section='autohotkey')

    def printPythonPath(self):
        logging.info('the python path:')
        logging.info(pformat(sys.path))


def isValidDir(path):
    """return the path, as str, if valid directory
    
    otherwise return ''
    """
    result = isValidPath(path, wantDirectory=True)
    return result        

def isValidFile(path):
    """return the path, as str, if valid file
    
    otherwise return ''
    """
    result = isValidPath(path, wantFile=True)
    return result        

def isValidPath(path, wantDirectory=None, wantFile=None):
    """return the path, as str, if valid
    
    otherwise return ''
    """
    if not path:
        return ''
    path = Path(path)
    path_expanded = Path(config.expand_path(str(path)))
    if wantDirectory:
        if path_expanded.is_dir():
            return str(path_expanded)
    elif wantFile:
        if path_expanded.is_file():
            return str(path_expanded)
    elif path.exists():
        return str(path_expanded)
    return ''


def createIfNotThere(path_name, level_up=None):
    """if path_name does not exist, but one up does, create.
    
    return the valid path (str) or
    False, if not a valid path
    if level_up, can create more step upward ( specify > 1)
    """
    level_up = level_up or 1
    dir_path = isValidDir(path_name)
    if dir_path:
        return dir_path
    start_path = config.expand_path(path_name)
    up_path = Path(start_path)

    level = level_up
    while level:
        up_path = up_path.parent
        if up_path.is_dir():
            break
        level -= 1
    else:
        print(f'cannot create directory, {level_up} level above should exist: "{str(up_path)}"')
        return False              
    Path(start_path).mkdir(parents=True)
    if path_name == start_path:
        print(f'created directory: "{start_path}"')
    else:
        print(f'created directory "{path_name}": "{start_path}"')
        
    return start_path

if __name__ == "__main__":
    _nc = NatlinkConfig()
    _config = _nc.Config
    _doc_path = _nc.documents_path
    _home_path = _nc.home_path
    _natlinkconfig_path = _nc.natlinkconfig_path
    print(f'natlinkconfig_path: {_natlinkconfig_path}')
    pass
