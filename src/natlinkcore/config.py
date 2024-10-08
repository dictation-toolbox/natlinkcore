#pylint:disable=C0114, C0115, C0116, R0913, E1101, R0911, R0914, W0702, R0912, C0209
import sys
import configparser
import logging
import os
from enum import IntEnum
from typing import List, Iterable, Dict
from pathlib import Path
import natlink

class NoGoodConfigFoundException(natlink.NatError):
    pass

class LogLevel(IntEnum):
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET


class NatlinkConfig:
    def __init__(self, directories_by_user: Dict[str, List[str]], 
                log_level: LogLevel, load_on_mic_on: bool,
                load_on_begin_utterance: bool, load_on_startup: bool, load_on_user_changed: bool):
        self.directories_by_user = directories_by_user  # maps user profile names to directories, '' for global
        self.log_level = log_level
        self.load_on_mic_on = load_on_mic_on
        self.load_on_begin_utterance = load_on_begin_utterance
        self.load_on_startup = load_on_startup
        self.load_on_user_changed = load_on_user_changed
        self.config_path = ''  # to be defined in from_config_parser
        # for convenience in other places:
        self.home_path = str(Path.home())
        self.documents_path = str(Path.home()/'Documents')

        #defaults for DAP configuration
        self.dap_enabled,self.dap_port,self.dap_wait_for_debugger_attach_on_startup = False,0,False
        
    def __repr__(self) -> str:
        return  f'NatlinkConfig(directories_by_user={self.directories_by_user}, ...)'

    @staticmethod
    def get_default_config() -> 'NatlinkConfig':
        return NatlinkConfig(directories_by_user={},
                             log_level=LogLevel.NOTSET,
                             load_on_mic_on=True,
                             load_on_begin_utterance=False,
                             load_on_startup=True,
                             load_on_user_changed=True)

    @property
    def directories(self) -> List[str]:
        dirs: List[str] = []
        for _u, directories in self.directories_by_user.items():
            dirs.extend(directories)
        return dirs

    def directories_for_user(self, user: str) -> List[str]:
        dirs: List[str] = []
        for u, directories in self.directories_by_user.items():
            if u in ['', user]:
                dirs.extend(directories)
        return dirs

    @staticmethod
    def from_config_parser(config: configparser.ConfigParser, config_path: str) -> 'NatlinkConfig':
        ret = NatlinkConfig.get_default_config()
        ret.config_path = config_path
        sections = config.sections()
        sp = sys.path   #handy, leave in for debugging

        dap_enabled, dap_port, dap_wait_for_debugger_attach_on_startup = (False,0,False)
    
        if config.has_section('settings.debugadapterprotocol'):
            dap_settings = config['settings.debugadapterprotocol']
            dap_enabled = dap_settings.getboolean('dap_enabled', fallback=False)
            dap_port = dap_settings.getint('dap_port', fallback=7474)
            dap_wait_for_debugger_attach_on_startup= dap_settings.getboolean('dap_wait_for_debugger_attach_on_startup', fallback=False)

        ret.dap_enabled,ret.dap_port,ret.dap_wait_for_debugger_attach_on_startup = \
            dap_enabled, dap_port, dap_wait_for_debugger_attach_on_startup


        for section in sections:
            if section.endswith('-directories'):
                user = section[:-len('-directories')]
                ret.directories_by_user[user] = list(config[section].values())
            elif section == 'directories':
                directories = []
                for name, directory in config[section].items():
                    if directory.find('site-packages') > 0:
                        package_name = Path(directory).stem
                        print(f'====Invalid input in configuration file "natlink.ini", section "directories":\n\tSkip name: {name}, directory: {directory}\n\tWhen you want to include a directory in site-packages, only specify the package name "{package_name}"')
                        continue
                    ## allow environment variables (or ~) in directory
                    directory_expanded = expand_path(directory)
                    if not os.path.isdir(directory_expanded):
                        print (f'from_config_parser: skip "{directory}" ("{name}"): is not a valid directory' if 
                            directory_expanded == directory 
                        else
                            f'from_config_parser: skip "{directory}" ("{name}"):\n\texpanded to directory "{directory_expanded}" is not a valid directory')
                        continue
                    directories.append(directory_expanded)

                ret.directories_by_user[''] =  directories 
        if config.has_section('settings'):
            settings = config['settings']
            level = settings.get('log_level')
            if level is not None:
                ret.log_level = LogLevel[level.upper()]
            ret.load_on_mic_on = settings.getboolean('load_on_mic_on', fallback=ret.load_on_mic_on)
            ret.load_on_begin_utterance = settings.getboolean('load_on_begin_utterance',
                                                              fallback=ret.load_on_begin_utterance)
            ret.load_on_startup = settings.getboolean('load_on_startup', fallback=ret.load_on_startup)
            ret.load_on_user_changed = settings.getboolean('load_on_user_changed', fallback=ret.load_on_user_changed)

        #default to no dap enabled.

 
        return ret

    @classmethod
    def from_file(cls, fn: str) -> 'NatlinkConfig':
        return cls.from_first_found_file([fn])

    @classmethod
    def from_first_found_file(cls, files: Iterable[str]) -> 'NatlinkConfig':
        isfile = os.path.isfile
        config = configparser.ConfigParser()
        for fn in files:
            if not isfile(fn):
                continue
            try:
                if config.read(fn):
                    return cls.from_config_parser(config, config_path=fn)
            except Exception as exc:
                mess = 'Error reading config file, %s\nPlease try to correct'% exc
                os.startfile(fn)
                raise OSError(mess) from exc
        # should not happen, because of DefaultConfig (was InstallTest)
        raise NoGoodConfigFoundException('No natlink config file found, please run configure natlink program\n\t(***configurenatlink***)')

def expand_path(input_path: str) -> str:
    r"""expand path if it starts with "~" or starts with an environment variable or name of python package
    
Paths can be:

- the name of a python package, or a sub directory of a python package
- natlink_settingsdir/...: the directory where natlink.ini is is searched for, either`%(NATLINK_SETTINGSDIR)` or `~/.natlink`
- `~/...`: the home directory
- Obsolete: natlink_userdir/...: instead natlink_settingsdir will be searched for, and a message is thrown. In the config program things are checked more thoroughly.
- some other environment variable: this environment variable is expanded 

The Documents directory can be found by "~\Documents"...

When there is nothing to expand, just return the input
    """
    expanduser, expandvars, normpath, isdir = os.path.expanduser, os.path.expandvars, os.path.normpath, os.path.isdir
    
    # I think, this is tackled below, input_path is one word, without slashes or ~ or %(...) (QH)
    # try:
    #     package_spec=u.find_spec(input_path)
    #     if package_spec is not None:
    #         package_path=str(p.Path(package_spec.origin).parent)
    #         return normpath(package_path)
    # except:
    #     pass
    if input_path.startswith('~'):
        home = expanduser('~')
        env_expanded = home + input_path[1:]
        # print(f'expand_path: "{input_path}" include "~": expanded: "{env_expanded}"')
        return normpath(env_expanded)

    ## "natlink_userdir" will go obsolete, to be replaced with "natlink_settingsdir" below:
    if input_path.startswith('natlink_userdir/') or input_path.startswith('natlink_userdir\\'):
        nud = expand_natlink_settingsdir()
        if isdir(nud):
            dir_path = input_path.replace('natlink_userdir', nud)
            dir_path = normpath(dir_path)
            if isdir(dir_path):
                return dir_path
            print(f'no valid directory found with "natlink_userdir": "{dir_path}"\nbut "natlink_userdir" should be replaced by "natlink_settingsdir" anyway')
            return dir_path
        print(f'natlink_userdir does not expand to a valid directory: "{nud}"\nbut "natlink_userdir" should be replaced by "natlink_settingsdir" anyway')
        return normpath(nud)

    if input_path.startswith('natlink_settingsdir/') or input_path.startswith('natlink_settingsdir\\'):
        nsd = expand_natlink_settingsdir()
        if isdir(nsd):
            dir_path = input_path.replace('natlink_settingsdir', nsd)
            dir_path = normpath(dir_path)
            if isdir(dir_path):
                return dir_path
            print(f'no valid directory found with "natlink_settingsdir": "{dir_path}"')
            return dir_path
        print(f'natlink_settingsdir does not expand to a valid directory: "{nsd}"')
        return normpath(nsd)
    
    
    # try if package:
    if input_path.find('/') > 0:
        package_trunk, rest = input_path.split('/', 1)
    elif input_path.find('\\') > 0:
        package_trunk, rest = input_path.split('\\', 1)
    else:
        package_trunk, rest = input_path, ''
        # find path for package.  not an alternative way without loading the package is to use importlib.util.findspec.
    
    # first check for exclude "C:" as trunk:
    if package_trunk and package_trunk[-1] != ":":
        try:
            pack = __import__(package_trunk)
            package_path = pack.__path__[-1]
            if rest:
                dir_expanded = str(Path(package_path)/rest)
                return dir_expanded
            return package_path
    
        except (ModuleNotFoundError, OSError):
            pass
    
    env_expanded = expandvars(input_path)
    # print(f'env_expanded: "{env_expanded}", from envvar: "{input_path}"')
    return normpath(env_expanded)

def expand_natlink_settingsdir():
    """Return the location of the natlink config files
    
    if NATLINK_SETTINGSDIR is set: return this, but... it should end with ".natlink"
    if NATLINK_SETTINGSDIR is NOT set: return `Path.home()/'.natlink'`
    """
    normpath = os.path.normpath
    nsd = os.getenv('natlink_settingsdir')
    if nsd:
        if not os.path.isdir(nsd):
            # this one should not happen, because .natlink is automatically created when it does not exist yet...
            raise OSError(f'Environment variable "NATLINK_SETTINGSDIR" should hold a valid directory, ending with ".natlink", not: "{nsd}"\n\tCreate your directory likewise or remove this environment variable, and go back to the default directory (~\\.natlink)\n')
            
        if not normpath(nsd).endswith('.natlink'):
            raise ValueError(f'Environment variable "NATLINK_SETTINGSDIR" should end with ".natlink", not: "{nsd}"\n\tCreate your directory likewise or remove this environment variable, returning to the default directory (~\\.natlink)\n')
    else:
        nsd = str(Path.home()/'.natlink')
        
    nsd = normpath(expand_path(nsd))
    # if not nsd.endswith('.natlink'):
    #     raise ValueError(f'expand_natlink_settingsdir: directory "{nsd}" should end with ".natlink"\n\tprobably you did not set the windows environment variable "NATLINK_SETTINGSDIR" incorrect, let it end with ".natlink".\n\tNote: if this ".natlink" directory does not exist yet, it will be created there.')
    return nsd
