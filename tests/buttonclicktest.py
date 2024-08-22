### buttonClick seems to cause an "ESP" runtime error with Dragon 16.
# via unimacroutils it runs via natlink.execScript

# via natlinkutils, the code runs (the right click is performed), but afterwards
# the "ESP" error is hit.

# When Dragon is running, it freezes, and must be closed with the windows task manager
# with release 5.5.7 this should be OK, because PlayEvents has been disabled.

import natlink
from natlinkcore import natlinkutils
from dtactions.unimacro import unimacroutils

if __name__ == "__main__":
    try:
        natlink.natConnect()
        print('try a buttonclick')
        unimacroutils.buttonClick('left', 2)
        print('after the buttonClick')
        
        print('now via natlinkutils.buttonClick (right click)')
        print('the code runs, but the "ESP" error window appears.')
        natlinkutils.buttonClick('right', 1)
        print('after the natlinkutils.buttonClick')
    finally:
        natlink.natDisconnect()
        
