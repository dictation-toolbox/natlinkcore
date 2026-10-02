#pylint:disable=C0302, W0702, R0904, C0116, W0613, R0914, R0912, R1732, W1514, W0107, W1203, W1309,
#pylint:disable=R0911, R0915, R1724, R1702
"""
natlinkconfigfunctions.py

This module performs the functions that configure Natlink with the different options and packages

These functions are called in different ways:
-Through the natlinkconfig_gui.py config GUI program (which calls functions in natlinkconfig_cli.py)
-Via the natlinkconfig_cli.py (CLI: command line interface, which calls functions in this module)
-By running natlinkconfig_cli in batch mode.

Quintijn Hoogenboom, January 2008 (...), August 2022, ... August 2026
"""

import os
import shutil
# from distutils.dir_util import copy_tree
import sys
import subprocess
from pprint import pformat, pprint
from pathlib import Path
import re
import configparser
import logging
try:
    from natlinkcore import natlinkstatus
except OSError:
    print('Error when starting natlinkconfigfunctions, cannot import natlinkstatus')
    pprint(sys.path)
    print('-'*80)
from natlinkcore import config
from natlinkcore import loader
from natlinkcore.readwritefile import ReadWriteFile
from natlinkcore import tkinter_dialogs


class NatlinkConfig:
    """performs the configuration tasks of Natlink
    
      setting UserDirectory, UnimacroDirectory and options, VocolaDirectory and options,
    DragonflyDirectory, Autohotkey options (ahk), and Debug option of Natlink.
    and also clearing the different directories.

    Changes are written in the config file, from which the path is taken from the loader instance.
    """
    def __init__(self,extra_pip_options=None):        

        ## extra_pip_options currently not used...
        self.extra_pip_options = [] if extra_pip_options is None else extra_pip_options
        self.do_pip_with_pre = '--pre' in self.extra_pip_options
        self.config_path = self.get_check_config_locations()
        self.config_dir = str(Path(self.config_path).parent)
        self.status = natlinkstatus.NatlinkStatus()
        self.Config = self.getConfig()  # get the config instance of config.NatlinkConfig
        # for convenience in other places:
        self.home_path = str(Path.home())
        self.documents_path = str(Path.home()/'Documents')
        self.natlinkconfig_path = config.expand_natlink_settingsdir()
        self.AllUscCommands = None # for vocola/dtactions
        pass
    
    def get_check_config_locations(self):
        
        """check the location/locations as given by the loader
        """
        config_path, fallback_path = loader.config_locations()  
        
        if not os.path.isfile(config_path):
            config_dir = Path(config_path).parent
            if not config_dir.is_dir():
                config_dir.mkdir(parents=True)
                
        # # #     ### here copy from previous location to current location,
        # # #     ### only if config_dir equals the new_default_config_dir and is empty
        # # #     (apart from directory Natlink for logging, set in line 10 of natlinkconfig_cli.py)
        # # #
        # # #     Are we satisfied with only copying natlink.ini if not present with the copyfile line below
        # # #     or do we want all the stuff in the old config directory???
        # # # 
        # # #     old_default_config_dir = config.expand_path(r'%personalhome%\.natlink')
        # # #     new_default_config_dir = config.expand_path(r'%localappdata%\Natlink')
        # # #     if str(config_dir) == new_default_config_dir and len(os.listdir(config_dir)) <= 1:
        # # #         copy_tree(old_default_config_dir, new_default_config_dir)
        # # # ## just in case the config_path still does not exist::
        if not os.path.isfile(config_path):
            shutil.copyfile(fallback_path, config_path)

        return config_path

    def check_config(self):
        """check config_file for possibly unwanted settings
        """
        # ensure the [directories] section is present:
        try:
            self.Config['directories']
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

        section = 'vocola'
        option = 'vocolatakeslanguages'
        try:
            value = self.Config[section][option]
            self.config_remove(section, option)
        except KeyError:
            pass
        
        section = 'vocola'
        old_option = 'vocolatakesunimacroactions'
        new_option = 'vocolatakesuniactions'
        try:
            old_value = self.Config[section][old_option]
            self.config_remove(section, old_option)
        except KeyError:
            pass
        else:
            try:
                _new_value = self.Config[section][new_option]
            except KeyError:
                self.config_set(section, new_option, old_value)
            
        pass
        # change the erroneus %personalhome% to %userprofile%
        old, new = "%personalhome%", "%userprofile%"
        for section in self.Config:
            for option in self.Config[section]:
                value = self.Config[section][option]
                
                if value.lower().startswith(old):
                    value  = new + value[len(old):]
                    self.config_set(section, option, value)
            
        if loader.had_msg_error:
            logging.error('The environment variable "NATLINK_USERDIR" has been changed to "NATLINK_SETTINGSDIR" by the user, but has a conclicting value')
            logging.error('Please remove "NATLINK_USERDIR", in the windows "environment variables", dialog User variables, and restart your program')

        if loader.had_msg_warning:
            logging.error('The key of the environment variable "NATLINK_USERDIR" should be changed to "NATLINK_SETTINGSDIR".')
            logging.error('You can do so in windows "environment variables", dialog "User variables".')
            
        
            
            
        # for key, value in self.Config[section].items():
        #     print(f'key: {key}, value: {value}')

    def getConfig(self):
        """return the config instance,
        """
        rwfile = ReadWriteFile()
        config_text = rwfile.readAnything(self.config_path)
        #disable any configuration, enabling using % sign in config values (QH, 30-07-2026)
        _config = configparser.ConfigParser(interpolation=None)
        _config.read_string(config_text)
        self.config_encoding = rwfile.encoding
        return _config

    def config_get(self, section, option):
        """set a setting into the natlink ini file

        """
        try:
            return self.Config.get(section, option)  # all interpolation is disabled
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
            with open(self.config_path, 'w', encoding='cp-1252') as fp:
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

        dir_path = str(dir_path).strip()
        directory = config.expand_path(dir_path)
        if directory is False:
            logging.error(f'Cannot expand dir_path: "{dir_path}"')
            return
        
        directory = createIfNotThere(dir_path, level_up=1)
        if not (directory and Path(directory).is_dir()):
            if dir_path == directory:
                logging.info(f'Cannot set "{option}", the given path is invalid: "{directory}"')
            else:
                logging.info(f'Cannot set "{option}", the given path is invalid: "{directory}" ("{dir_path}")')
            return
        
        nice_dir_path = self.prefix_home_appdata(dir_path)
        nice_dir_path = nice_dir_path.replace('/', '\\')        
        self.config_set(section, option, nice_dir_path)
        dir_path = dir_path.strip()
        directory = createIfNotThere(dir_path, level_up=1)
        if not (directory and Path(directory).is_dir()):
            logging.warning(f'Cannot set directory "{option}", the given path is invalid: "{directory}" ("{dir_path}")')
        
        self.config_remove('previous settings', option)
        if nice_dir_path == dir_path:
            if section == 'directories':
                logging.info(f'Set option "{option}" to "{dir_path}"')
            else:
                logging.info(f'Set in section "{section}", option "{option}" to "{dir_path}"')
        else:
            if section == 'directories':
                logging.info(f'Set option "{option}" to "{nice_dir_path}" (expanding to "{dir_path}")')
            else:
                logging.info(f'Set in section "{section}", option "{option}" to "{nice_dir_path}" (expanding to "{dir_path}")')
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
 
 
    def prefix_home_appdata(self, dir_path):
        r"""if dir_path startswith home directory, replace this with "%userprofile% (instead of "~")
        
        Same if dir_path startswith the path of you local appdata directory, change to %localappdata%.
        
        tested in test_prefix_home_appdata (tests\test_natlinkconfig.py)
        """
        home_path = str(Path.home())
        homepath_env = os.path.expandvars('%userprofile%')
        if home_path != homepath_env:
            logging.warning(f'The environment variable "%userprofile%" ("{homepath_env}")\n   is NOT EQUAL to "Path.home" ("{home_path}")')
        
        
        appdataLocal = os.path.expandvars('%localappdata%')
        if dir_path.startswith(appdataLocal):
            dir_path = dir_path.replace(appdataLocal, '%localappdata%')
            return dir_path


        appdataRoaming = rf'{home_path}\AppData\Roaming'
        if dir_path.startswith(appdataRoaming):
            dir_path = dir_path.replace(appdataRoaming, '%appdata%')
            return dir_path

        if dir_path.startswith(home_path):
            dir_path = dir_path.replace(home_path, "%userprofile%")
            
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
        
    def pip_package(self, package, params, do_pre=None):
        """
        Run a pip command with possible pre option
        Diagnostic logging.3
        
        """
        # this check is in the natlinkconfig_cli:
        # result = self.check_elevated_mode()
        # print(f'result of check_elevated_mode: {result}')
        # if not result:
        #     return
        command = [sys.executable,"-m", "pip"]
        command.append('install')
        command.append(package)
        ## premature option:::
        # if do_pre or self.do_pip_with_pre:
        #     command.append("--pre")
        command.extend(params)
        logging.info(f' pip command:  {command} ')
        completed_process = subprocess.run(command,capture_output=True)
        logging.debug(f' completed_process:  {completed_process}')
        completed_process.check_returncode()


    def enable_unimacro(self, arg):
        unimacro_user_dir = self.status.getUnimacroUserDirectory()
        if unimacro_user_dir and os.path.isdir(unimacro_user_dir):
            logging.info(f'UnimacroUserDirectory is already defined: "{unimacro_user_dir}"\n\tto change, first clear (option "O") and then set again')
            logging.info('\nWhen you want to upgrade Unimacro, also first clear ("O"), then choose this option ("o") again.\n')
            return False

        uni_dir = self.status.getUnimacroDirectory()
        if uni_dir:
            logging.info('==== instal and/or update unimacro====\n')
            params = ["--upgrade"]
            try:
                self.pip_package("unimacro", params, self.do_pip_with_pre)
            except subprocess.CalledProcessError:
                logging.info('====\ncould not pip install --upgrade unimacro\n====\n')
                return False
        else:
            params = []
            try:
                self.pip_package("unimacro", params, self.do_pip_with_pre)
            except subprocess.CalledProcessError:
                logging.info('====\ncould not pip install unimacro\n====\n')
                return False
        self.status.refresh()   # refresh status
        uni_dir = self.status.getUnimacroDirectory()

        self.setDirectory('UnimacroUserDirectory', arg, section='unimacro')
        unimacro_user_dir = self.config_get('unimacro', 'unimacrouserdirectory')
        if not unimacro_user_dir:
            logging.warning(f' strange error, installing unimacro seemed to word,'
                             ' but cannot find unimacro_user_dir in the inifile "{natlink.ini}"')
            return False
        uniGrammarsDir = r'unimacro\unimacrogrammars'
        self.setDirectory('unimacrodirectory','unimacro')  #always unimacro

        self.setDirectory('unimacrogrammarsdirectory', uniGrammarsDir)
        return True

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
        if dragonfly_user_dir and os.path.isdir(dragonfly_user_dir):
            logging.info(f'DragonflyUserDirectory is already defined: "{dragonfly_user_dir}"\n\tto change, first clear (option "D") and then set again')
            logging.info('\nWhen you want to upgrade Dragonfly, also first clear ("D"), then choose this option ("d") again.\n')
            return

        df_dir = self.status.getDragonflyDirectory()
        if df_dir:
            logging.info('==== instal and/or update dragonfly2====\n')            
            params = ["--upgrade"]
            try:
                self.pip_package("dragonfly2", params, self.do_pip_with_pre)
            except subprocess.CalledProcessError:   
                logging.info('====\ncould not pip install --upgrade dragonfly2\n====\n')
                return
        else:
            params = []
            try:
                self.pip_package("dragonfly2",params, self.do_pip_with_pre)
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
        self.status.refresh()
        vocola_user_dir = self.status.getVocolaUserDirectory()
        if self.status.vocolaIsEnabled(): 
        # if vocola_user_dir and isdir(vocola_user_dir):
            logging.info(f'VocolaUserDirectory is already defined: "{vocola_user_dir}"\n\tto change, first clear (option "V") and then set again')
            logging.info('\nWhen you want to upgrade Vocola (vocola2), also first clear ("V"), then choose this option ("v") again.\n')
            return

        voc_dir = self.status.getVocolaDirectory()
        if voc_dir:
            logging.info('==== install --update vocola2====\n')            
            params = ["--upgrade"]
            try:
                self.pip_package("vocola2", params, self.do_pip_with_pre)
            except subprocess.CalledProcessError:   
                logging.info('====\ncould not pip install --upgrade vocola2\n====\n')
                return
        else:
            logging.info('==== install vocola2====\n')            
            params = []
            try:
                self.pip_package("vocola2",params, self.do_pip_with_pre)
            except subprocess.CalledProcessError:
                logging.info('====\ncould not pip install vocola2\n====\n')
                return
        # self.status.refresh()   # refresh status
        voc_dir = self.status.getVocolaDirectory()

        self.setDirectory('VocolaUserDirectory', arg, section='vocola')
        vocola_user_dir = self.config_get('vocola', 'VocolaUserDirectory')
        if not vocola_user_dir:
            return
        # vocGrammarsDir = self.status.getVocolaGrammarsDirectory()
        vocGrammarsDir = config.expand_path(r'natlink_settingsdir\vocolagrammars', must_exist=False)
        if not vocGrammarsDir:
            logging.error('Could not expand directory for vocola grammars')
            return
        vocGrammarsPath = Path(vocGrammarsDir)
        if not vocGrammarsPath.is_dir():
            parent = vocGrammarsPath.parent
            if parent.is_dir():
                vocGrammarsPath.mkdir()
                assert vocGrammarsPath.is_dir()
            else:
                logging.error(f'vocolaGrammarsDirectory is not a valid directory: "{vocGrammarsDir}"')
                return          
            
        self.setDirectory('vocoladirectory','vocola2')  #always vocola2
        self.setDirectory('vocolagrammarsdirectory', vocGrammarsDir)    
        createIfNotThere(vocGrammarsDir)

        if self.status.getVocolaTakesUniactions():
            self.copyUniactionsIncludeFile()
            self.removeUniactionsVchLineInVocolaFiles(keepValidIncludeLines=True)
            self.includeUniactionsVchLineInVocolaFiles()
        else:
            self.removeUniactionsVchLineInVocolaFiles()
            
        # with new language versios ordering of directories, paths to include lines can be broken:
        # invalid include lines are commented out.
        self.checkVocolaIncludeLines()  # previous obsolete lines, but also current, with language versions.
        self.status.refresh()

    def disable_vocola(self, arg=None):
        """disable vocola, arg not needed/used
        """
        self.clearDirectory('VocolaUserDirectory', section='vocola')
        self.config_remove('directories', 'vocolagrammars')
        self.config_remove('directories', 'vocolagrammarsdirectory')   # could still be there
        self.config_remove('directories', 'vocola')
        self.config_remove('directories', 'vocoladirectory')   #could still be there...

    disable_vocola2 = disable_vocola

    def copyUniactionsIncludeFile(self):
        """copy Uniactions include file into Vocola user directory
        """
        uacFile = 'Uniactions.vch'
        # also remove the previous version Unimacro.vch
        # also remove usc.vch from VocolaUserDirectory
        dtactionsDir = Path(self.status.getDtactionsDirectory())
        fromFolder = Path(dtactionsDir)/'Vocola_compatibility'
        toFolder = Path(self.status.getVocolaUserDirectory())
        if not dtactionsDir.is_dir():
            mess = f'copyUniactionsIncludeFile: dtactionsDir "{str(dtactionsDir)}" is not a directory'
            logging.warning(mess)
            return
        fromFile = fromFolder/uacFile
        if not fromFile.is_file():
            mess = f'copyUniactionsIncludeFile: file "{str(fromFile)}" does not exist (is not a valid file)'
            logging.warning(mess)
            return
        if not toFolder.is_dir():
            mess = f'copyUniactionsIncludeFile: vocolaUserDirectory does not exist "{str(toFolder)}" (is not a directory)'
            logging.warning(mess)
            return
        
        toFile = toFolder/uacFile
        if toFolder.is_file():
            logging.info(f'remove previous "{str(toFile)}"')
            try:
                os.remove(toFile)
            except:
                mess = f'copyUniactionsIncludeFile: Could not remove previous version of "{str(toFile)}"'
                logging.info(mess)
        try:
            shutil.copyfile(fromFile, toFile)
            logging.info(f'copied "{uacFile}" from "{str(fromFolder)}" to "{str(toFolder)}"')
        except:
            mess = f'Could not copy new version of "{uacFile}", from "{str(fromFolder)}" to "{str(toFolder)}"'
            logging.warning(mess)
            return
        return

    def removeUniactionsIncludeFile(self, keepValidIncludeLines=None):
        """remove Unimacro include file from Vocola user directory

        """
        uscFiles = ['Unimacro.vch', 'Uniactions.vch', 'usc.vch']
        # also remove previous files unimacro.vch and usc.vch from VocolaUserDirectory
        toFolder = Path(self.status.getVocolaUserDirectory())
        if not toFolder.is_dir():
            mess = f'removeUniactionsIncludeFile: vocolaUserDirectory does not exist "{str(toFolder)}" (is not a directory)'
            logging.warning(mess)
            return
        for f in uscFiles:
            toFile = toFolder/f
            if toFile.is_file():
                logging.info(f'remove Uniactions include file "{str(toFile)}"')
                try:
                    os.remove(toFile)
                except:
                    mess = f'copyUniactionsIncludeFile: Could not remove previous version of "{str(toFile)}"'
                    logging.warning(mess)

       
    def checkVocolaIncludeLines(self):
        """do an include or a removal of these lines in all current Vocola files
        
        This should be carried out at enable of Vocola and
        at change of the option "a", VocolaTakesUniactions
        
        Also check possible problems with paths to include lines ("../enx", "..", ...)
        that can arise with changed (multiple languages) configurations.
        
        Vocola must be enabled.
        """
        if not self.status.vocolaIsEnabled():
            return
        if self.status.getVocolaTakesUniactions():
            self.removeUniactionsVchLineInVocolaFiles(keepValidIncludeLines=True)
            self.includeUniactionsVchLineInVocolaFiles()
        else:
            self.removeUniactionsVchLineInVocolaFiles()
        self.checkVocolaIncludeLinesValidPath()

    def includeUniactionsVchLineInVocolaFiles(self, subFolder=None):
        """include the Uniactions wrapper support line into all Vocola command files
        
        Do this for the VocolaUserDirectory and sub directories (of non english languages,
        "nld", "esp", etc).
        
        Check the .vcl files, ignore .vch header files.
        
        The call from the natlinkconfig_cli (and therefore natlinkconfig_gui) should be
        without the subFolder specified.
        (tested in test_vocola_uniactions_include_lines_on_and_off and
        test_vocola_include_lines_take_uniactions_off (test_natlinkconfig.py))
        """
        uacFile = 'Uniactions.vch'
        includeLine = f'include {uacFile};'  # for 'enx' language
          
        todoFolder = self.status.getVocolaUserDirectory()

        recursive = bool(subFolder)
        if recursive:
            # recursive call, non enx directories:
            includeLine = f'include ..\\{uacFile};'
            todoFolder = os.path.join(todoFolder, subFolder)
            if not os.path.isdir(todoFolder):
                return False
            
        if not os.path.isdir(todoFolder):
            mess = f'cannot find Vocola command files directory, not a valid path: {todoFolder}'
            logging.warning(mess)
            return mess
        changedFilesLanguage = 0
        changedFiles = 0
        for f in os.listdir(todoFolder):
            F = os.path.join(todoFolder, f)
            if f.endswith(".vcl"):
                got_include_line = False
                Output = []
                rwfile = ReadWriteFile()
                for line in rwfile.readAnythingLines(F):
                    Output.append(line)
                    if line == includeLine:
                        got_include_line = True
                if not got_include_line:
                    Output.insert(0, includeLine)
                    rwfile.writeAnything(F, Output)
                    changedFiles += 1
            elif len(f) == 3:
                changedFilesLanguage = self.includeUniactionsVchLineInVocolaFiles(subFolder=f)

        # self.disableVocolaTakesUniactions()
        if recursive:
            if changedFiles:
                mess = f'Put include line in {changedFiles} files in language folder {subFolder}'
                return changedFiles
        else:
            if changedFiles:
                mess = f'Put include line in {changedFiles} files in {todoFolder} ("enx" language)'
                logging.warning(mess)
            
            changedFiles += changedFilesLanguage
            # if changedFiles:
            #     mess = f'Total changed {changedFiles} files in {todoFolder} and sub folders'
            #     
            #     logging.warning(mess)

        return True
    
    
    def removeUniactionsVchLineInVocolaFiles(self, keepValidIncludeLines=None, subFolder=None):
        """remove the Uniactions wrapper support line into all Vocola command files
        
        remove all include lines to "Uniactions.vch" and previous names of this file.
        
        Do this for safety before includeUniactionsVchLineInVocolaFiles!
        
        todoFolder is called with recursive calls when language sub directories exist...
        """
        uscFiles = ['Uniactions.vch', 'usc.vch', 'Unimacro.vch']
        # also remove includes of usc.vch
        todoFolder = self.status.getVocolaUserDirectory()
        recursive = bool(subFolder)
        validIncludeLine = 'include Uniactions.vch;' if keepValidIncludeLines else ''
        
        
        
        toRemoveLines = []
        for inc in uscFiles:
            toRemoveLines.append(f'include {inc};')
            toRemoveLines.append(fr'include ..\{inc};')
            toRemoveLines.append(fr'include ..\{inc};')
            toRemoveLines.append(f'include ../{inc};')

        if recursive:
            # language subfolder
            validIncludeLine = 'include ..\\Uniactions.vch;' if keepValidIncludeLines else ''
                
            todoFolder  = os.path.join(todoFolder, subFolder)
            if not os.path.isdir(todoFolder):
                return True

        if not os.path.isdir(todoFolder):
            mess = f'cannot find Vocola command files directory, not a valid path: {todoFolder}'
            logging.warning(mess)
            return False
        changedFiles = 0
        changedFilesLanguage = 0
        
        for f in os.listdir(todoFolder):
            F = os.path.join(todoFolder, f)
            if f.endswith(".vcl"):
                changed = 0
                Output = []
                firstLine = True
                
                rwfile = ReadWriteFile()
                for line in rwfile.readAnythingLines(F):
                    if firstLine and keepValidIncludeLines:
                        # keep the valid include line if at top of the file:
                        if line.strip() == validIncludeLine:
                            firstLine = False
                            continue
                    firstLine = False
                    for oldLine in toRemoveLines:
                        if line.strip().lower() == oldLine.lower():
                            changed = 1
                            break
                    else:
                        Output.append(line)
                if changed:
                    # had break, so changes were made:
                    rwfile.writeAnything(F, Output)
                    changedFiles += 1
            elif len(f) == 3:
                changedFilesLanguage  = self.removeUniactionsVchLineInVocolaFiles(keepValidIncludeLines=keepValidIncludeLines,
                                                                                  subFolder=f)
                if isinstance(changedFilesLanguage, int):
                    changedFiles += changedFilesLanguage
        # self.disableVocolaTakesUniactions()
        if recursive:
            if changedFiles:
                mess = f'Removed invalid Uniactions include line in {changedFiles} files in language folder {subFolder}'
        else:
            if changedFiles:
                mess = f'Removed invalid Uniactions include line from {changedFiles} files in {todoFolder} ("enx" language)'
                logging.info(mess)

        return True
    
    def checkVocolaIncludeLinesValidPath(self, subFolder=None):
        """check validity of include lines in vocola command files.
        
        Also correct Unimacro(...) commands into Usc(...).
        errors can be caused with new multi languages configurations, the "enx" directory is no
        longer available.

        """
        isfile, join = os.path.isfile, os.path.join
        todoFolder = self.status.getVocolaUserDirectory()
        recursive = bool(subFolder)

        if recursive:
            todoFolder  = os.path.join(todoFolder, subFolder)
            if not os.path.isdir(todoFolder):
                return True

        if not os.path.isdir(todoFolder):
            mess = f'cannot find Vocola command files directory, not a valid path: {todoFolder}'
            logging.warning(mess)
            return False
        changedFiles = 0
        changedFilesLanguage = 0
        
        for f in os.listdir(todoFolder):
            F = os.path.join(todoFolder, f)
            if f.endswith(".vcl") or f.endswith(".vch"):
                changes = 0
                Output = []
                rwfile = ReadWriteFile()
                for line in rwfile.readAnythingLines(F):
                    if (not (line.startswith('include')) or line.startswith('#invalidfile#')) or  line.find('=') > 0:
                        # hard to check whether line is changed or not, so add to it:
                        newLine = line.replace('Unimacro(', 'Usc(') if line.find('Unimacro(') > 0 else line
                        changes += self.outputReportChange(Output, newLine, oldLine=line)
                        continue
                    incRelPath = line.split(maxsplit=1)[1].replace(';', '').strip()
                    incRelPath = incRelPath.strip('"').strip("'").strip('"')
                    incRelPath = incRelPath.replace('/', '\\')
                    if isfile(join(todoFolder, incRelPath)):
                        newLine = f'include {incRelPath};'
                        changes += self.outputReportChange(Output, newLine, oldLine=line)
                        continue
                    if recursive:
                        # change ..\\enx to ..\\
                        if incRelPath.startswith('..\\enx'):
                            incRel2 = incRelPath.replace('\\enx', '')
                            if isfile(join(todoFolder, incRel2)):
                                newLine = f'include {incRel2};'
                                changes += self.outputReportChange(Output, newLine, oldLine=line)
                                continue
                    else:
                        if incRelPath.startswith('..\\'):
                            incRel2 = incRelPath.replace('..\\', '')
                            if isfile(join(todoFolder, incRel2)):
                                newLine = f'include {incRel2};'
                                changes += self.outputReportChange(Output, newLine, oldLine=line)
                                continue
                    # incRelPath NOT a file:
                    newLine = f'#invalidfile#include {incRelPath};' 
                    changes += self.outputReportChange(Output, newLine, oldLine=line)

                if changes:
                    # had break, so changes were made:
                    rwfile.writeAnything(F, Output)
                    changedFiles += 1
            elif len(f) == 3:
                changedFilesLanguage  = self.checkVocolaIncludeLinesValidPath(subFolder=f)
                if isinstance(changedFilesLanguage, int):
                    changedFiles += changedFilesLanguage
        # self.disableVocolaTakesUniactions()
        if recursive:
            if changedFiles:
                mess = f'Changed path of include line in {changedFiles} files in language folder {subFolder}'
        else:
            if changedFiles:
                mess = f'Changed path of include line in {changedFiles} files in {todoFolder} ("enx" language)'
                logging.info(mess)

        return True
    
    def outputReportChange(self, Output, newLine, oldLine):
        """return 1 if line changed, 0 otherwise
        """
        Output.append(newLine)
        return int(newLine.strip() != oldLine)

    def checkUscLinesInVocolaFiles(self, subFolder=None):
        """check vocola files for invalid or commented Usc commands
        
        When VocolaTakesUniactions is switched on, commented previous lines with Usc
        should be re-activated. This is only done in .vcl files,
        header files .vch are kept outside this check.
        Older command lines with previous "Unimacro" prefix are changed into "Usc"
        """
        join, isdir = os.path.join, os.path.isdir
        todoFolder = self.status.getVocolaUserDirectory()
        UscIsOn = self.status.getVocolaTakesUniactions()
        
        recursive = bool(subFolder)
        todoFolder = self.status.getVocolaUserDirectory()

        if recursive:
            changedFilesLanguage = 0
            todoFolder = join(todoFolder, subFolder)
            if not os.path.isdir(todoFolder):
                return False
            
        if not isdir(todoFolder):
            mess = f'cannot find Vocola command files directory, not a valid path: {todoFolder}'
            logging.warning(mess)
            return mess
        changedFiles = 0
        for f in os.listdir(todoFolder):
            F = os.path.join(todoFolder, f)
            if f.endswith(".vcl"):
                got_changes = 0
                multiple_command = []
                Output = []

                rwfile = ReadWriteFile()
                for line in rwfile.readAnythingLines(F):
                    if UscIsOn:    #remove #Usc%# comments no need of mutiline commands
                        corrected_line = self.CorrectLineUsc(line, UscIsOn)
                    else:
                        if line.startswith('#') or not line.strip():
                            if multiple_command:
                                multiple_command.append(line)
                                continue
                        if not line.rstrip().endswith(";"):
                            multiple_command.append(line)
                            continue
                        # end multiple command lines:
                        # if one line (normal case) multiple_command will only contain this line
                        multiple_command.append(line)
                        
                        corrected_line = self.CorrectLineUsc(multiple_command, UscIsOn)
                        multiple_command = []
                    if corrected_line != line:
                        got_changes += 1
                        Output.append(corrected_line)
                    else:
                        Output.append(line)
                if got_changes:
                    rwfile.writeAnything(F, Output)

                    mess = f'correcting .vcl file enx in {f}, {got_changes} changes'
                    logging.debug(mess)
                    changedFiles += 1
            elif len(f) == 3:
                changedFilesLanguage = self.checkUscLinesInVocolaFiles(subFolder=f)
                if changedFilesLanguage:
                    mess = f'correcting .vcl file "{subFolder}\\{f}": {changedFilesLanguage} changed'
                    logging.info(mess)
                    changedFiles  += changedFilesLanguage
        
        
        if recursive:
            return changedFilesLanguage
        
        if not recursive:
            mess = f'correcting .vcl files, changed {changedFiles} files in {todoFolder} and sub folders'
            logging.info(mess)

        return True

    def getUscCommands(self):
        """get a list of all Usc commands, put in "AllUscCommands"
        
        Include Unimacro.
        """
        join, isfile = os.path.join, os.path.isfile
        if self.AllUscCommands is not None:
            return self.AllUscCommands
        File = join(self.status.getDtactionsDirectory(), 'vocola_compatibility', 'Uniactions.vch')
        assert isfile(File)
        Commands = {'Unimacro', 'Usc'}
        rwfile = ReadWriteFile()
        for line in rwfile.readAnythingLines(File):
            if line.startswith('#'):
                continue
            if line.find('(') > 0:
                com = line.split('(', 1)[0]
                Commands.add(com)
        if not Commands:
            logging.warning('getUscCommands, no Usc command lines found in {File}.')
            self.AllUscCommands = []
            return []
        self.AllUscCommands = list(Commands)
        return self.AllUscCommands
            

    def CorrectLineUsc(self, lines, uscIsOn):
        """correct vocola line, depending on the uscIsOn variable
        
        tests in test_vocola_regular_expressions (test_natlinkconfig.py)
        """
        UscCommands = self.getUscCommands()
        assert isinstance(UscCommands, list)
        assert len(UscCommands) > 0
        
        insideBrackets = '|'.join(UscCommands)
        reExpr = rf'\b({insideBrackets})[(]'
        reUsc = re.compile(reExpr)
        
        reOldPrefix = re.compile(r'\b(Unimacro)(?=\()')
        Comment = "#Usc#"
        if uscIsOn:
            # just removing #Usc# from commented lines:
            assert isinstance(lines, str)
            line = lines
            if line.startswith(Comment):
                line = line[5:]
                
            if not line.startswith('#') and line.find('=') > 0:
                # try to change "Unimacro" into "Usc"
                com, act = line.split('=', 1)
                m = reOldPrefix.search(act)
                if m:
                    act2 = act.replace('Unimacro(', 'Usc(')
                    line = f'{com}={act2}'
            return line

        # UscIsOff, making #Usc# comment lines
        # this can be multiline!!!
        if isinstance(lines, str):
            lines = [lines]
        had_equal = False
        has_usc = False
        multiple = []
        # commandPart = line.split('=', 1)[1]
        for li in lines:
            if li.startswith('#'):
                multiple.append(li)
                continue
            m = None
            if not had_equal and li.find('=') > 0:
                act = li.split('=', 1)[1]
                had_equal = True
                m = reUsc.search(act)
                has_usc = has_usc or bool(m)
            elif had_equal:
                m = reUsc.search(li)
                has_usc = has_usc or bool(m)
        if has_usc:
            lines = [l.replace('Unimacro(', 'Usc(') for l in lines]
            lines = [Comment + l for l in lines if not l.startswith(Comment)]
        return '\n'.join(lines)
                    
        


    # def enableVocolaTakesLanguages(self):
    #     """setting registry  so Vocola can divide different languages
    # 
    #     """
    #     key = "vocolatakeslanguages"
    #     self.config_set('vocola', key, 'True')
    #     
    # 
    # def disableVocolaTakesLanguages(self):
    #     """disables so Vocola cannot take different languages
    #     """
    #     key = "vocolatakeslanguages"
    #     self.config_set('vocola', key, 'False')

    def enableVocolaTakesUniactions(self):
        """do setting, so Vocola can take Unimacro Actions
        
        1. copy the include file "Uniactions.vch" to the VocolaUserDirectory
        2. remove invalid and older variants of the include file line (keep the current!)
        3. insert an include line in each vocola command file
           
        """
        key = "VocolaTakesUniactions"
        if not self.status.vocolaIsEnabled():
            print('\n==========================\nenableVocolaTakesUniactions: Vocola is not enabled, please enable Vocola first!\n')
            return
        
        self.config_set('vocola', key, 'True')
        # this one is to ensure that erroneous or old include lines are removed:
        self.removeUniactionsVchLineInVocolaFiles(keepValidIncludeLines=True)
        self.includeUniactionsVchLineInVocolaFiles()
        self.checkUscLinesInVocolaFiles()
        # remove previous versions...
        self.removeUniactionsIncludeFile()
        self.copyUniactionsIncludeFile()

    def disableVocolaTakesUniactions(self):
        """disables this option, so Vocola does not take Uniactions any more
        
        Remove "Uniactions.vch" and the include lines in each .vcl file
        """
        key = "VocolaTakesUniactions"

        if not self.status.vocolaIsEnabled():
            print('\n==========================\ndisableVocolaTakesUniactions: Vocola is not enabled, please enable Vocola first!\n')
            return

        self.config_set('vocola', key, 'False')
        self.removeUniactionsVchLineInVocolaFiles()
        self.checkUscLinesInVocolaFiles()
        self.removeUniactionsIncludeFile()
        
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
    if dir_path and Path(dir_path).is_dir():
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

def get_folder_dict(folderpath):
    """return the contenst in a dict, assume all text files
    
    rstrip all lines
    """
    join = os.path.join
    D = {}
    folderdir = str(folderpath)
    len_prefix = len(folderdir)
    
    for dirpath, _dirnames, files in os.walk(folderdir):
        # print(f'Found directory: {dirpath}')
        subdir = dirpath[len_prefix+1:]
        key_prefix = f'{subdir}---' if subdir else ''
        for fi in files:
            with open(join(dirpath, fi), 'r') as f:
                lines = [line.rstrip(' \n') for line in f if line.strip()]
            D[key_prefix + fi] = lines if len(lines) <= 20 else '> 20 lines'
            
    return D


if __name__ == "__main__":
    _nc = NatlinkConfig()
    _config = _nc.Config
    _doc_path = _nc.documents_path
    _home_path = _nc.home_path
    _natlinkconfig_path = _nc.natlinkconfig_path
    print(f'natlinkconfig_path: {_natlinkconfig_path}')
    pass
