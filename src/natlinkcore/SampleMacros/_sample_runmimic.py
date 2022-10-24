#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
#pylint:disable=C0115, C0116, W0613
"""_sample_runmimic.py

This script tests the commands with alternatives in interactive mode

August 2022, with new python3 release coming, this test works.

1. Load this file in one of your "directories"
2. Toggle your microphone
3. Say: "mimic runzero".

Expected output:

Heard macro "mimic run_zero", "['mimic', 'runzero']"
Heard macro "mimic run_one", "['mimic', 'north']"
Heard macro "mimic run_two", "['mimic', 'table']"

"""
import natlink
from natlinkcore.natlinkutils import GrammarBase

class ThisGrammar(GrammarBase):

    gramSpec = """
        <run_zero> exported = mimic runzero;
        <run_one> exported = mimic (north | east | south | west) ;
        <run_two> exported = mimic {furniture}[(north | east | south | west)+];
    """
    
    def initialize(self):
        self.load(self.gramSpec)
        self.setList('furniture', ['table', 'chair'])
        self.activateAll()

    def gotResults_run_zero(self,words,fullResults):
        print(f'\nHeard macro "mimic run_zero", "{words}"')
        natlink.recognitionMimic(['mimic', 'north'])
    
    def gotResults_run_one(self,words,fullResults):
        print(f'Heard macro "mimic run_one", "{words}"')
        natlink.recognitionMimic(['mimic', 'table'])
        
    def gotResults_run_two(self,words,fullResults):
        print(f'Heard macro "mimic run_two", "{words}"')
        
thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    #pylint:disable=W0603
    global thisGrammar
    if thisGrammar:
        thisGrammar.unload()
    thisGrammar = None
