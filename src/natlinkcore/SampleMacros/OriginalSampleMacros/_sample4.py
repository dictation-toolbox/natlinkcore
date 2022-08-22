#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# _sample4.py
#   Sample macro file d\xe9mostrating mouse movement.
#
# Put in MacroSystem folder and toggle the microphone.
#
import natlink
from natlinkcore.natlinkutils import *

class ThisGrammar(GrammarBase):

    gramSpec = """
        <start> exported = demo sample four;
    """

    def gotResults_start(self,words,fullResults):
        # execute a control-left drag down 30 pixels
        print('_sample4 start: drags an item down 30 pixels... (needs checking!!)')
        x,y = natlink.getCursorPos()
        natlink.playEvents( [ (wm_keydown,vk_control,1),
                              (wm_lbuttondown,x,y),
                              (wm_mousemove,x,y+30),
                              (wm_lbuttonup,x,y+30),
                              (wm_keyup,vk_control,1) ] )
        
    def initialize(self):
        self.load(self.gramSpec)
        self.activateAll()

thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    #pylint:disable=W0603
    global thisGrammar
    if thisGrammar:
        thisGrammar.unload()
    thisGrammar = None




