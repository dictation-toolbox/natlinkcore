"""some dialogs running with tkinter

GetDirFromDialog(title, initialdir)  both optional. initialdir, default:home directory)
return a directory path (str), or '' if dialog was canceled.

GetFileFromDialog(title, filetypes, initialdir), all optional.

    filetypes is a tuple of tuples, like:
          (('Python files', '*.py;*.pyw'), ('text files', '*.txt'), ('All files', '*.*'))
  
          default is:  (('text files', '*.txt'),('All files', '*.*'))
returns a path to the file (str).

Note: all paths are with forward slashes.

"""
import os
from tkinter import filedialog
from tkinter import *

from natlinkcore import config

def GetDirFromDialog(title="Please choose a directory", initialdir=None):
    """call the directory dialog via tkinter

    initialdir is directory to start with, can be "expanded" with "~" or
    environment variables, defaults to the current directory if not passed
        
    return a valid path (directory) or None if canceled
    """
    if initialdir:
        initialdir = config.expand_path(initialdir)
        if not os.path.isdir(initialdir):
            print(f'not a directory: "{initialdir}", start with home directory')
            initialdir = None
    if not initialdir:
        initialdir = config.expand_path("~")
    root = Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title=title, initialdir=initialdir)

    return folder_selected.replace('/', '\\')

    
def GetFileFromDialog(title="Please choose a file", filetypes=None, initialdir=None):
    """call the file dialog via wxPython
        
    return a valid path (file) or None if dialog was canceled
    """
    # pylint: disable=E1101
    if filetypes is None:
        filetypes = filetypes or (('text files', '*.txt'),('All files', '*.*'))
    elif not isinstance(filetypes, tuple):
        raise TypeError(f'GetFileFromDialog, filetypes should be a tuple of filetypes, not: {filetypes}')
    
    if initialdir:
        initialdir = config.expand_path(initialdir)
        if not os.path.isdir(initialdir):
            print(f'GetFileFromDialog, not a directory: "{initialdir}", start with home directory')
            initialdir = None
    if not initialdir:
        initialdir = config.expand_path("~")

    root = Tk()
    root.withdraw()
    folder_selected = filedialog.askopenfilename(title=title, initialdir=initialdir, filetypes=filetypes)
    
    
    return folder_selected.replace('/', '\\')

if __name__ == "__main__":
    result = GetDirFromDialog(title="Please specify a directory", initialdir="~/.natlink")
    print(f'GetDirFromDialog, result: {result}')

    result = GetFileFromDialog(title="Please specify a file", initialdir="~/Documents/Quintijn/Robert")
    print(f'GetFileFromDialog, result: {result}')

    Filetypes = (('Excel files', '*.xlsx;*.xls'), ('text files', '*.txt'), ('All files', '*.*'), ('Python files', '*.py;*.pyw'))
    result = GetFileFromDialog(title="Please specify a file", initialdir="~/Documents/Quintijn/Robert", filetypes=Filetypes)
    print(f'GetFileFromDialog, result: {result}')

    Filetypes = (('Python files', '*.py;*.pyw'), ('text files', '*.txt'), ('All files', '*.*'))
    result = GetFileFromDialog(title="Please specify a file", initialdir="/projects/miscqh", filetypes=Filetypes)
    print(f'GetFileFromDialog, result: {result}')
    
    