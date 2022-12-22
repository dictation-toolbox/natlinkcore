#pylint:disable=R0904
import sys
import getopt
import cmd
import os
import os.path
from natlinkcore.configure import extensions_and_folders

from natlinkcore.configure import natlinkconfigfunctions

def _main(Options=None):
    """Catch the options and perform the resulting command line functions

    options: -i, --info: give status info

             -I, --reginfo: give the info in the registry about Natlink
             etc., usage above...

    """
    cli = CLI()
    cli.Config = natlinkconfigfunctions.NatlinkConfig()
    shortOptions = "DVNOHKaAiIxXbBuqe"
    shortArgOptions = "d:v:n:o:h:k:"
    if Options:
        if isinstance(Options, str):
            Options = Options.split(" ", 1)
        Options = [_.strip() for _ in  Options]
    else:
        Options = sys.argv[1:]

    try:
        options, args = getopt.getopt(Options, shortOptions+shortArgOptions)
    except getopt.GetoptError:
        print(f'invalid option: {Options}')
        cli.usage()
        return

    if args:
        print(f'should not have extraneous arguments: {args}')
    for o, v in options:
        o = o.lstrip('-')
        funcName = f'do_{o}'
        func = getattr(cli, funcName, None)
        if not func:
            print(f'option "{o}" not found in cli functions: "{funcName}"')
            cli.usage()
            continue
        if o in shortOptions:
            func(None) # dummy arg
        elif o in shortArgOptions:
            func(v)
        else:
            print('options should not come here')
            cli.usage()


          
class CLI(cmd.Cmd):
    """provide interactive shell control for the different options.
    """
    def __init__(self, Config=None):
        cmd.Cmd.__init__(self)
        self.prompt = '\nNatlink config> '
        self.info = "type 'u' for usage"
        self.Config = None
        self.message = ''
        # if __name__ == "__main__":
        #     print("Type 'u' for usage ")

    def stripCheckDirectory(self, dirName):
        """allow quotes in input, and strip them.
        
        Return "" if directory is not valid
        """
        if not dirName:
            return ""
        n = dirName.strip()
        while n and n.startswith('"'):
            n = n.strip('"')
        while n and n.startswith("'"):
            n = n.strip("'")
        if n:
            n.strip()
        
        if os.path.isdir(n):    
            return n
        print(f'not a valid directory: "{n}" ({dirName})')
        return ''

    def usage(self):
        """gives the usage of the command line options or options when
        the command line interface  (CLI) is used
        """
        print('-'*60)
        print(r"""Use either from the command line like 'natlinkconfigfunctions.py -i'
or in an interactive session using the CLI (command line interface). 

[Status]

i       - info, print information about the Natlink status
I       - show the natlink.ini file (in Notepad), you can manually edit.
j       - print PythonPath variable

[Natlink]

x/X     - enable/disable debug output of Natlink

[Vocola]

v/V     - enable/disable Vocola by setting/clearing VocolaUserDirectory,
          where the Vocola Command Files (.vcl) will be located.
          (~ or %HOME% are allowed, for example "~/.natlink/VocolaUser")

b/B     - enable/disable distinction between languages for Vocola user files
a/A     - enable/disable the possibility to use Unimacro actions in Vocola

[Unimacro]

o/O     - enable/disable Unimacro, by setting/clearing the UnimacroUserDirectory, where
          the Unimacro user INI files are located, and several other directories (~ or %HOME% allowed)

[DragonflyDirectory]
d/D     - enable/disable the DragonflyDirectory, the directory where
          you can put your Dragonfly scripts (UserDirectory can also be used)

[UserDirectory]
n/N     - enable/disable UserDirectory, the directory where
          User Natlink grammar files are located (e.g., "~\UserDirectory")

[AutoHotkey]
h/H     - set/clear the AutoHotkey exe directory.
k/K     - set/clear the User Directory for AutoHotkey scripts.
[Extensions]
e       - give a list of python modules registered as extensions.
[Other]

u/usage - give this list
q       - quit

help <command>: give more explanation on <command>
        """)
        print('='*60)

    # info----------------------------------------------------------
    def do_i(self, arg):
        self.Config.status.__init__()
        S = self.Config.status.getNatlinkStatusString()
        S = S + '\n\nIf you changed things, you must restart Dragon'
        print(S)
    def do_I(self, arg):
        # inifile natlinkstatus.ini settings:
        self.Config.status.__init__()
        self.Config.openConfigFile()
    def do_j(self, arg):
        # print PythonPath:
        
        self.Config.printPythonPath()

    def do_e(self,arg):
        print("extensions and folders for registered natlink extensions:")
        ef=""
        for n,f in extensions_and_folders():
            ef+= f"\n{n} {f}" 
        print(ef)

    def help_i(self):
        print('-'*60)
        print("""The command info (i) gives an overview of the settings that are
currently set inside the Natlink system.

With command (I), you open the file "natlink.ini"

The command (j) gives the PythonPath variable which should contain several
Natlink directories after the config GUI runs succesfully

Settings are set by either the Natlink/Vocola/Unimacro installer
or by functions that are called by the CLI (command line interface).

After you change settings, restart Dragon.
""")
        print('='*60)
    help_j = help_I = help_i
    
    # User Directory, Dragonfly directory -------------------------------------------------
    # for easier remembering, change n to d (DragonFly)
    def do_d(self, arg):
        self.Config.enable_dragonfly(arg)
    
    def do_D(self, arg):
        self.Config.disable_dragonfly(arg)

    def do_n(self, arg):
        self.Config.setDirectory('UserDirectory', arg)
    
    def do_N(self, arg):
        self.Config.clearDirectory('UserDirectory')
    
    def help_n(self):
        print('-'*60)
        print('''Sets (n [<path>]) or clears (N) the "UserDirectory" of Natlink.
This is the folder where your own python grammar files are/will be located.
''')
    def help_d(self):
        print('-'*60)
        print('''Sets (d [<path>]) or clears (D) the "DragonflyUserDirectory".
This is the folder where your own Dragonfly python grammar files are/will be located.
''')
        
    help_N = help_n
    help_D = help_d
    
    # Unimacro User directory and Editor or Unimacro INI files-----------------------------------
    def do_o(self, arg):
        self.Config.enable_unimacro(arg)
        
            
    def do_O(self, arg):
        self.Config.disable_unimacro()

    def help_o(self):
        print('-'*60)
        print(r"""set/clear UnimacroUserDirectory (o <path>/O)


Setting this directory also enables Unimacro. Clearing it disables Unimacro

In this directory, your user INI files (and possibly other user
dependent files) will be put.

You can use (if entered through the CLI) "~" for user home directory, or
another environment variable (%%...%%). (example: "o ~\Documents\UnimacroUser")
""")
        print('='*60)

    help_O = help_o

    # Unimacro Command Files Editor-----------------------------------------------
    # not needed for Aaron's GUI:
    # def do_p(self, arg):
    #     self.message = "Set Unimacro INI file editor"
    #     print(f'do action: {self.message}')
    #     key = "UnimacroIniFilesEditor"
    #     self.Config.setFile(key, arg, section='unimacro')
    #         
    # def do_P(self, arg):
    #     self.message = "Clear Unimacro INI file editor, go back to default Notepad"
    #     print(f'do action: {self.message}')
    #     key = "UnimacroIniFilesEditor"
    #     self.Config.clearFile(key, section='unimacro')

    # Unimacro Vocola features-----------------------------------------------
    # managing the include file wrapper business.
    # can be called from the Vocola compatibility button in the config GUI.
#     def do_l(self, arg):
#         self.message = "Copy include file Unimacro.vch into Vocola User Directory"
#         print(f'do action: {self.message}')
#         self.Config.copyUnimacroIncludeFile()
# 
#     def help_l(self):
#         print('-'*60)
#         print("""Copy Unimacro.vch header file into Vocola User Files directory      (l)
# 
# Insert/remove 'include Unimacro.vch' lines into/from each Vocola 
# command file                                                        (m/M)
# 
# Using Unimacro.vch, you can call Unimacro shorthand commands from a
# Vocola command.
# """)
#         print('='*60)
# 
#     def do_m(self, arg):
#         self.message = 'Insert "include Unimacro.vch" line in each Vocola Command File'
#         print(f'do action: {self.message}')
#         self.Config.enableVocolaTakesUnimacroActions()
#         
#     def do_M(self, arg):
#         self.message = 'Remove "include Unimacro.vch" line from each Vocola Command File'
#         print(f'do action: {self.message}')
#         self.Config.removeUnimacroVchLineInVocolaFiles()
#         print('and do action: disableVocolaTakesUnimacroActions')
#         self.Config.disableVocolaTakesUnimacroActions()
#         
#     help_m = help_M = help_l
    
    
    # Vocola and Vocola User directory------------------------------------------------
    def do_v(self, arg):
        """specify the VocolaUserDirectory,
        
        but the config needs also the VocolaDirectory and the VocolaGrammarsDirectory
        """
        self.Config.enable_vocola(arg)
                    
    def do_V(self, arg):
        """disable Vocola, arg not needed
        """
        self.Config.disable_vocola(arg)
        

    def help_v(self):
        print('-'*60)
        print(r"""Enable/disable Vocola by setting/clearing the VocolaUserDirectory
(v <path>/V).

In this VocolaUserDirectory your Vocola Command File are/will be located.

""")
        print('='*60)

    help_V = help_v
    

    # enable/disable Natlink debug output...
    def do_x(self, arg):
        self.message = 'Print debug output to "Messages from Natlink" window'
        print(f'do action: {self.message}')

        self.Config.setLogging('DEBUG')
    def do_X(self, arg):
        self.message = 'Disable printing debug output to "Messages from Natlink" window'
        print(f'do action: {self.message}')
        self.Config.setLogging('INFO')

    def help_x(self):
        print('-'*60)
        print("""Enable (x)/disable (X) Natlink debug output

This sends (sometimes lengthy) debug messages to the
"Messages from Natlink" window. Effectively this sets the
logging variable to "DEBUG" or "INFO"
""")
        print('='*60)

    help_X = help_x
    
    # different Vocola options
    def do_b(self, arg):
        self.message = "Enable Vocola different user directories for different languages"
        print(f'do action: {self.message}')
        self.Config.enableVocolaTakesLanguages()
    def do_B(self, arg):
        self.message = "Disable Vocola different user directories for different languages"
        print(f'do action: {self.message}')
        self.Config.disableVocolaTakesLanguages()

    def do_a(self, arg):
        self.message = "Enable Vocola taking Unimacro actions"
        print(f'do action: {self.message}')
        self.Config.enableVocolaTakesUnimacroActions()
        
    def do_A(self, arg):
        self.message = "Disable Vocola taking Unimacro actions"
        print(f'do action: {self.message}')
        self.Config.disableVocolaTakesUnimacroActions()

    def help_a(self):
        print('-'*60)
        print("""----Enable (a)/disable (A) Vocola taking Unimacro actions.
        
These actions (Unimacro Shorthand Commands) and "meta actions" are processed by
the Unimacro actions module (really dtactions)
""")
        print('='*60)
        
    def help_b(self):
        print('-'*60)
        print("""----Enable (b)/disable (B) different Vocola User Directories

If enabled, Vocola will look into a subdirectory "xxx" of
VocolaUserDirectory IF the language code of the current user speech
profile is "xxx" and  is NOT "enx".

So for English users this option will have no effect.

The first time a command file is opened in, for example, a
Dutch speech profile (language code "nld"), a subdirectory "nld" 
is created, and all existing Vocola Command files for this Dutch speech profile are copied into this folder.

When you use your English speech profile again, ("enx") the Vocola Command files in the VocolaUserDirectory are taken again.
""")
        print('='*60)

    help_B = help_b
    help_A = help_a

    # autohotkey settings:
    def do_h(self, arg):
        self.message = f'set directory of AutoHotkey.exe to: "{arg}"'
        print(f'do action: {self.message}')
        self.Config.setAhkExeDir(arg)

    def do_H(self, arg):
        self.message = 'clear directory of AutoHotkey.exe, return to default'
        print(f'do action: {self.message}')
        self.Config.clearAhkExeDir()

    def do_k(self, arg):
        self.message = f'set user directory for AutoHotkey scripts to: "{arg}"'
        print(f'do action: {self.message}')
        self.Config.setAhkUserDir(arg)

    def do_K(self, arg):
        self.message = 'clear user directory of AutoHotkey scripts, return to default'
        print(f'do action: {self.message}')
        self.Config.clearAhkUserDir()
            
    def help_h(self):
        print('-'*60)
        print("""----Set (h)/clear (return to default) (H) the AutoHotkey exe directory.
       Assume autohotkey.exe is found there (if not AutoHotkey support will not be there)
       If set to a invalid directory, AutoHotkey support will be switched off.
       
       Set (k)/clear (return to default) (K) the User Directory for AutoHotkey scripts.
       
       Note: currently these options can only be run from the natlinkconfigfunctions.py script.
""")
        print('='*60)

    help_H = help_k = help_K = help_h

    # enable/disable Natlink debug output...

    def default(self, line):
        print(f'no valid entry: "{line}", type "u" or "usage" for list of commands')
        print()

    def do_quit(self, arg):
        sys.exit()
    do_q = do_quit
    def do_usage(self, arg):
        self.usage()
    do_u = do_usage
    def help_u(self):
        print('-'*60)
        print("""u and usage give the list of commands
lowercase commands usually set/enable something
uppercase commands usually clear/disable something
Informational commands: i and I
""")
    help_usage = help_u


def main_cli():
    if len(sys.argv) == 1:
        Cli = CLI()
        Cli.Config = natlinkconfigfunctions.NatlinkConfig()
        Cli.info = ""
        print('\nWelcome to the NatlinkConfig Command Line Interface\n')
        print('Type "I" for manual editing the "natlink.ini" config file\n')
        print('Type "u" for Usage\n')
        try:
            Cli.cmdloop()
        except (KeyboardInterrupt, SystemExit):
            pass

if __name__ == "__main__":
    main_cli()
else:
    _main()
    