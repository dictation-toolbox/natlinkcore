### a buttonClick via natlink.execScript results in a runtimeerror (with Dragon 16)
#
# #  File "C:\Program Files (x86)\Natlink\site-packages\natlink\__init__.py", line 82, in execScript
# #     return _execScript(script_w,args)
# # natlink.SyntaxError: Error 63334 compiling script execScript (line 1)


import natlink
from dtactions.unimacro import unimacroutils


if __name__ == "__main__":
    try:
        natlink.natConnect()
        print('try a buttonclick via execScript')
        unimacroutils.buttonClick('left', 2)
        print('after the buttonClick via execScript')
    finally:
        natlink.natDisconnect()
        
