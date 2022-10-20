#
# natlinkconfigfunctions.py

#   This module performs the configuration functions.
#   called from nalinkgui (a PySimpleGUI window)),
#   or CLI, see below
#
#   Quintijn Hoogenboom, January 2008 (...), August 2022
#

#pylint:disable=C0302, W0702, R0904, C0116, W0613, R0914, R0912, C0415, W0611
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
from pprint import pprint
from pathlib import Path
import configparser

from natlinkcore import natlinkstatus
from natlinkcore import config
from natlinkcore import loader
from natlinkcore import readwritefile
from natlinkcore import tkinter_dialogs

isfile, isdir, join = os.path.isfile, os.path.isdir, os.path.join

class NatlinkConfig:
    """performs the configuration tasks of Natlink
    
    setting UserDirectory, UnimacroDirectory and options, VocolaDirectory and options,
    DragonflyDirectory, Autohotkey options (ahk), and Debug option of Natlink.
    and also clearing the different directories.

    Changes are written in the config file, from which the path is taken from the loader instance.
    """
    def __init__(self):
        self.config_path = self.get_check_config_locations()
        self.config_dir = str(Path(self.config_path).parent)
        self.status = natlinkstatus.NatlinkStatus()
        self.Config = self.getConfig()  # get the config instance of config.NatlinkConfig
        self.check_config()
        # for convenience in other places:
        self.home_path = str(Path.home())
        self.documents_path = str(Path.home()/'Documents')
        self.natlinkconfig_path = config.expand_natlink_userdir()

    def get_check_config_locations(self):
        """check the location/locations as given by the loader
        """
        config_path, fallback_path = loader.config_locations()
        
        if isfile(config_path):
            with open(config_path, 'r', encoding='utf-8') as fp:
                text = fp.read().strip()
            if not text:
                print(f'empty natlink.ini file: "{config_path}",\n\tremove, and go back to default')
                os.remove(config_path)
        
        if not isfile(config_path):
            config_dir = Path(config_path).parent
            if not config_dir.is_dir():
                config_dir.mkdir(parents=True)
            shutil.copyfile(fallback_path, config_path)
        return config_path

    def check_config(self):
        """check config_file for possibly unwanted settings
        """
        self.config_remove(section='directories', option='default_config')
        keys = self.config_get('directories')
        
        ## check vocola:
        if 'vocoladirectory' in keys and 'vocolagrammarsdirectory' in keys:
            try:
                import vocola2
            except ImportError:
                # vocola has been gone, remove:
                self.disable_vocola()
                self.config_remove('vocola', 'vocolauserdirectory')
        else:
            ## just to be sure:
            self.config_remove('vocola', 'vocolauserdirectory')
            self.config_remove('directories', 'vocoladirectory')
            self.config_remove('directories', 'vocolagrammarsdirectory')

        if 'unimacrodirectory' in keys and 'unimacrogrammarsdirectory' in keys:
            try:
                import unimacro
            except ImportError:
                # unimacro has been gone, remove:
                self.disable_unimacro()
                self.config_remove('unimacro', 'unimacrouserdirectory')
        else:
            ## just to be sure:
            self.config_remove('unimacro', 'unimacrouserdirectory')
            self.config_remove('directories', 'unimacrodirectory')
            self.config_remove('directories', 'unimacrogrammarsdirectory')
        

        if 'dragonflyuserdirectory' in keys:
            try:
                import dragonfly
            except ImportError:
                # dragonfly has been gone, remove:
                self.disable_dragonfly()
                
    def getConfig(self):
        """return the config instance
        """
        rwfile = readwritefile.ReadWriteFile()
        config_text = rwfile.readAnything(self.config_path)
        _config = configparser.ConfigParser()
        _config.read_string(config_text)
        self.config_encoding = rwfile.encoding
        return _config

    def config_get(self, section, option=None):
        """get the section keys or a setting from the natlink ini file

        """
        if option:
            try:
                return self.Config.get(section, option)
            except (configparser.NoSectionError, configparser.NoOptionError):
                return None
        return self.Config.options(section)
 
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
        self.status.__init__()
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
        self.status.__init__()

    # def setUserDirectory(self, arg):
    #     self.setDirectory('UserDirectory', arg)
    # def clearUserDirectory(self, arg):
    #     self.clearDirectory('UserDirectory')
        

    def setDirectory(self, option, dir_path, section=None):
        """set the directory, specified with "key", to dir_path
        """
        section = section or 'directories'
        if not dir_path:
            print('==== Please specify the wanted directory in Dialog window ====\n')
            prev_path = self.config_get('previous settings', option) or self.documents_path
            dir_path = tkinter_dialogs.GetDirFromDialog(title=f'Please choose a "{option}"', initialdir=prev_path)
            if not dir_path:
                print('No valid directory specified')
                return

        dir_path = dir_path.strip().replace('/', '\\')
        directory = createIfNotThere(dir_path, level_up=1)
        if not (directory and Path(directory).is_dir()):
            if directory is False:
                directory = config.expand_path(dir_path)
            if dir_path == directory:
                print(f'Cannot set "{option}", the given path is invalid: "{directory}"')
            else:
                print(f'Cannot set "{option}", the given path is invalid: "{directory}" ("{dir_path}")')
            return
        
        nice_dir_path = self.prefix_home(dir_path)
        nice_dir_path = nice_dir_path.replace('/', '\\')        
        self.config_set(section, option, nice_dir_path)
        self.config_remove('previous settings', option)
        if section == 'directories':
            print(f'Set option "{option}" to "{dir_path}"')
        else:
            print(f'Set in section "{section}", option "{option}" to "{dir_path}"')
        return
        
    def clearDirectory(self, option, section=None):
        """clear the setting of the directory designated by option
        """
        section = section or 'directories'
        old_value = self.config_get(section, option)
        if not old_value:
            print(f'The "{option}" was not set, nothing changed...')
            return
        if isValidDir(old_value):
            self.config_set('previous settings', option, old_value)
        else:
            self.config_remove('previous settings', option)
            
        self.config_remove(section, option)
        print(f'cleared "{option}"')
 
 
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
                print('No valid file specified')
                return
        file_path = file_path.strip()
        if not Path(file_path).is_file():
            print(f'No valid file specified ("{file_path}")')
            
        self.config_set(section, option, file_path)
        self.config_remove('previous settings', option)
        print(f'Set in section "{section}", option "{option}" to "{file_path}"')
        return
        
    def clearFile(self, option, section):
        """clear the setting of the directory designated by option
        """
        old_value = self.config_get(section, option)
        if not old_value:
            print(f'The "{option}" was not set, nothing changed...')
            return
        if isValidFile(old_value):
            self.config_set('previous settings', option, old_value)
        else:
            self.config_remove('previous settings', option)
            
        self.config_remove(section, option)
        print(f'cleared "{option}"')
  

    def setLogging(self, logginglevel):
        """Sets the natlink logging output
        logginglevel (str) -- CRITICAL, FATAL, ERROR, WARNING, INFO, DEBUG
        
        This one is used in the natlinkconfig_gui
        """
        key = 'log_level'
        section = 'settings'        
        value = logginglevel.upper()
        old_value = self.config_get(section, key)
        if old_value == value:
            print(f'setLogging, setting is already "{old_value}"')
            return True
        if value in ["CRITICAL", "FATAL", "ERROR", "WARNING", "INFO", "DEBUG"]:
            print(f'setLogging, setting logging to: "{value}"')
            self.config_set(section, key, value)
            if old_value is not None:
                self.config_set('previous settings', key, old_value)
            return True
        print(f'Invalid value for setLogging: "{value}"')
        return False

    def enable_unimacro(self, arg):
        unimacro_user_dir = self.status.getUnimacroUserDirectory()
        if unimacro_user_dir and isdir(unimacro_user_dir):
            print(f'UnimacroUserDirectory is already defined: "{unimacro_user_dir}"\n\tto change, first clear (option "O") and then set again')
            print('\nWhen you want to upgrade Unimacro, also first clear ("O"), then choose this option ("o") again.\n')
            return

        uni_dir = self.status.getUnimacroDirectory()
        if uni_dir:
            print('==== install and/or update unimacro====\n')            
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "unimacro"])
            except subprocess.CalledProcessError:
                print('====\ncould not pip install --upgrade unimacro\n====\n')
                return
        else:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "unimacro"])
            except subprocess.CalledProcessError:
                print('====\ncould not pip install unimacro\n====\n')
                return
        self.status.refresh()   # refresh status
        uni_dir = self.status.getUnimacroDirectory()

        self.setDirectory('UnimacroUserDirectory', arg, section='unimacro')
        unimacro_user_dir = self.config_get('unimacro', 'unimacrouserdirectory')
        if not unimacro_user_dir:
            return
        uniGrammarsDir = r'natlink_userdir\unimacrogrammars'
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


    def enable_vocola(self, arg):
        """enable vocola, by setting arg (prompting if False), and other settings
        """
        vocola_user_dir = self.status.getVocolaUserDirectory()
        if vocola_user_dir and isdir(vocola_user_dir):
            print(f'VocolaUserDirectory is already defined: "{vocola_user_dir}"\n\tto change, first clear (option "V") and then set again')
            print('\nWhen you want to upgrade Vocola (vocola2), also first clear ("V"), then choose this option ("v") again.\n')
            return

        voc_dir = self.status.getVocolaDirectory()
        if voc_dir:
            print('==== install and/or update vocola2====\n')
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "vocola2"])
            except subprocess.CalledProcessError:
                print('====\ncould not pip install --upgrade vocola2\n====\n')
                return
        else:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "vocola2"])
            except subprocess.CalledProcessError:
                print('====\ncould not pip install vocola2\n====\n')
                return
        self.status.refresh()   # refresh status
        voc_dir = self.status.getVocolaDirectory()

        self.setDirectory('VocolaUserDirectory', arg, section='vocola')
        vocola_user_dir = self.config_get('vocola', 'VocolaUserDirectory')
        if not vocola_user_dir:
            return
        # vocGrammarsDir = self.status.getVocolaGrammarsDirectory()
        vocGrammarsDir = r'natlink_userdir\vocolagrammars'
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

    def enable_dragonfly(self, arg):
        """enable dragonfly, by setting arg (prompting if False), and other settings
        """
        key = 'dragonflyuserdirectory'
        dragonfly_user_dir = self.status.getDragonflyUserDirectory()
        if dragonfly_user_dir and isdir(dragonfly_user_dir):
            print(f'dragonflyUserDirectory is already defined: "{dragonfly_user_dir}"\n\tto change, first clear (option "D") and then set again')
            print('\nWhen you want to upgrade dragonfly (dragonfly2), also first clear ("D"), then choose this option ("d") again.\n')
            return

        dfl_prev_dir = self.config_get('previous settings', key)
        if dfl_prev_dir:

            print('==== install and/or update dragonfly2====\n')
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "dragonfly2"])
            except subprocess.CalledProcessError:
                print('====\ncould not pip install --upgrade dragonfly2\n====\n')
                return
        else:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "dragonfly2"])
            except subprocess.CalledProcessError:
                print('====\ncould not pip install dragonfly2\n====\n')
                return
        self.status.refresh()   # refresh status

        self.setDirectory(key, arg)

    def disable_dragonfly(self, arg=None):
        """disable dragonfly, arg not needed/used
        """
        key = 'dragonflyuserdirectory'
        self.clearDirectory(key)

    def copyUnimacroIncludeFile(self):
        """copy Unimacro include file into Vocola user directory

        """
        uscFile = 'Unimacro.vch'
        # also remove usc.vch from VocolaUserDirectory
        unimacroDir = Path(self.status.getUnimacroDirectory())
        fromFolder = Path(unimacroDir)/'Vocola_compatibility'
        toFolder = Path(self.status.getVocolaUserDirectory())
        if not unimacroDir.is_dir():
            mess = f'copyUnimacroIncludeFile: unimacroDir "{str(unimacroDir)}" is not a directory'
            print(mess)
            return
        fromFile = fromFolder/uscFile
        if not fromFile.is_file():
            mess = f'copyUnimacroIncludeFile: file "{str(fromFile)}" does not exist (is not a valid file)'
            print(mess)
            return
        if not toFolder.is_dir():
            mess = f'copyUnimacroIncludeFile: vocolaUserDirectory does not exist "{str(toFolder)}" (is not a directory)'
            print(mess)
            return
        
        toFile = toFolder/uscFile
        if toFolder.is_file():
            print(f'remove previous "{str(toFile)}"')
            try:
                os.remove(toFile)
            except:
                mess = f'copyUnimacroIncludeFile: Could not remove previous version of "{str(toFile)}"'
                print(mess)
        try:
            shutil.copyfile(fromFile, toFile)
            print(f'copied "{uscFile}" from "{str(fromFolder)}" to "{str(toFolder)}"')
        except:
            mess = f'Could not copy new version of "{uscFile}", from "{str(fromFolder)}" to "{str(toFolder)}"'
            print(mess)
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
            print(mess)
            return
        
        toFile = toFolder/uscFile
        if toFolder.is_file():
            print(f'remove Unimacro include file "{str(toFile)}"')
            try:
                os.remove(toFile)
            except:
                mess = f'copyUnimacroIncludeFile: Could not remove previous version of "{str(toFile)}"'
                print(mess)

    def includeUnimacroVchLineInVocolaFiles(self, subDirectory=None):
        """include the Unimacro wrapper support line into all Vocola command files
        
        as a side effect, set the variable for Unimacro in Vocola support:
        VocolaTakesUnimacroActions...
        """
        uscFile = 'Unimacro.vch'
        oldUscFile = 'usc.vch'
##        reInclude = re.compile(r'^include\s+.*unimacro.vch;$', re.MULTILINE)
##        reOldInclude = re.compile(r'^include\s+.*usc.vch;$', re.MULTILINE)
        
        # also remove includes of usc.vch
        toFolder = self.status.getVocolaUserDirectory()
        if subDirectory:
            toFolder = os.path.join(toFolder, subDirectory)
            includeLine = f'include ..\\{uscFile};\n'
        else:
            includeLine = f'include {uscFile};\n'
        oldIncludeLines = [f'include {oldUscFile};',
                           f'include ..\\{oldUscFile};',
                           f'include {uscFile.lower()};',
                           f'include ..\\{uscFile.lower()};',
                           ]
            
        if not os.path.isdir(toFolder):
            mess = f'cannot find Vocola command files directory, not a valid path: {toFolder}'
            print(mess)
            return mess
        nFiles = 0
        for f in os.listdir(toFolder):
            F = os.path.join(toFolder, f)
            if f.endswith(".vcl"):
                changed = 0
                correct = 0
                Output = []
                rwfile = readwritefile.ReadWriteFile()
                lines = rwfile.readAnything(F).split('\n')
                for line in lines:
                    if line.strip() == includeLine.strip():
                        correct = 1
                    if line.strip() in oldIncludeLines:
                        changed = 1
                        continue
                    Output.append(line)
                if changed or not correct:
                    # changes were made:
                    if not correct:
                        Output.insert(0, includeLine)
                    rwfile.writeAnything(F, Output)
                    nFiles += 1
            elif len(f) == 3 and os.path.isdir(F):
                # subdirectory, recursive
                self.includeUnimacroVchLineInVocolaFiles(F)
        mess = f'changed {nFiles} files in {toFolder}'
        print(mess)
        return True

    def removeUnimacroVchLineInVocolaFiles(self, subDirectory=None):
        """remove the Unimacro wrapper support line into all Vocola command files
        """
        uscFile = 'Unimacro.vch'
        oldUscFile = 'usc.vch'
##        reInclude = re.compile(r'^include\s+.*unimacro.vch;$', re.MULTILINE)
##        reOldInclude = re.compile(r'^include\s+.*usc.vch;$', re.MULTILINE)
        
        # also remove includes of usc.vch
        if subDirectory:
            # for recursive call language subfolders:
            toFolder = subDirectory
        else:
            toFolder = self.status.getVocolaUserDirectory()
            
        oldIncludeLines = [f'include {oldUscFile};',
                           f'include ..\\{oldUscFile};',
                           f'include {uscFile};',
                           f'include ..\\{uscFile};',
                           f'include ../{oldUscFile};',
                           f'include ../{uscFile};',
                           f'include {uscFile.lower()};',
                           f'include ..\\{uscFile.lower()};',
                           f'include ../{uscFile.lower()};'
                           ]

            
        if not os.path.isdir(toFolder):
            mess = f'cannot find Vocola command files directory, not a valid path: {toFolder}'
            print(mess)
            return mess
        nFiles = 0
        for f in os.listdir(toFolder):
            F = os.path.join(toFolder, f)
            if f.endswith(".vcl"):
                changed = 0
                Output = []
                rwfile = readwritefile.ReadWriteFile()
                lines = rwfile.readAnything(F).split('\n')

                for line in lines:
                    for oldLine in oldIncludeLines:
                        if line.strip() == oldLine:
                            changed = 1
                            break
                    else:
                        Output.append(line)
                if changed:
                    # had break, so changes were made:
                    rwfile.writeAnything(F, Output)
                    nFiles += 1
            elif len(f) == 3 and os.path.isdir(F):
                self.removeUnimacroVchLineInVocolaFiles(F)
        mess = f'removed include lines from {nFiles} files in {toFolder}'
        print(mess)

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
        os.startfile(self.config_path)
        print(f'opened "{self.config_path}" in a separate window')
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
        print('the python path:')
        pprint(sys.path)


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
