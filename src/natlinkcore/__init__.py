'''Python portion of Natlink, a compatibility module for Dragon Naturally Speaking
The python stuff including test modules'''

import importlib.metadata

__version__ = importlib.metadata.version(__package__)  #version set in pyproject.toml now.

#pylint:disable=
from pathlib import Path

def getThisDir(fileOfModule):
    """get directory of calling module
    """
    return Path(fileOfModule).parent
def logname():
    """ Returns the name of the logger module, which is simply 'natlink'.  An entry point is defined for this in pyproject.toml.
    """
    return "natlink"
# warningTexts = []
# def warning(text):
#     """print warning only once, if warnings is set!
#     
#     warnings can be set in the calling functions above...
#     """
#     textForeward = text.replace("\\", "/")
#     if textForeward in warningTexts:
#         return
#     warningTexts.append(textForeward)
#     print(text)
#     
