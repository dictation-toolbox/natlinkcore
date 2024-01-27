'''Python portion of Natlink, a compatibility module for Dragon Naturally Speaking
The python stuff including test modules'''
__version__="5.3.8"
#pylint:disable=
from pathlib import Path

def getThisDir(fileOfModule):
    """get directory of calling module
    """
    return Path(fileOfModule).parent

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
