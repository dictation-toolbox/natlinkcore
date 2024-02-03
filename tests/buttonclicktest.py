### buttonClick seems to cause an "ESP" runtime error with Dragon 16.

import natlink
from dtactions.unimacro import unimacroutils

if __name__ == "__main__":
    try:
        natlink.natConnect()
        print('try a buttonclick')
        natlinkutils.buttonClick('left', 1)
        print('after the buttonClick')
    finally:
        natlink.natDisconnect()
        
