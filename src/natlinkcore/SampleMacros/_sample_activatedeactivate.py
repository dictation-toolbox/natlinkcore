#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
#pylint:disable=C0115, C0116, W0613, W0201
"""_sample_runmimic.py

This script tests the commands of activating rules in interactive mode

January 2024, with possible changes with DPI16.

1. Load this file in one of your "directories" (or add this directory to your natlink.ini file in directories section)
2. Toggle your microphone
3. give commands like "show result", active rule number (one, two, three), deactivate rule number,
   activateset number (one, two), deactivate set number,
   activate all, deactivate all

4. special case: activate all except, all rules except 'ruleone' and 'ruletwo' are activated... (leaving 'rulethree' active)
   
   You can test the availability of one of the three rules by calling "test rule one" etc.
   
   setone = ['ruleone', 'rulethree']
   settwo = ['ruletwo', 'rulethree']

"""
# import natlink
import copy
from natlinkcore.natlinkutils import GrammarBase

class ThisGrammar(GrammarBase):

    gramSpec = """
        <activaterule> exported = activate rule {rulelist};
        <activateset> exported = activate set {setlist};
        <activateall> exported = activate all;
        <activateallexcept> exported = activate all except;
        <deactivaterule> exported = deactivate rule {rulelist};
        <deactivateset> exported = deactivate set {setlist};
        <deactivateall> exported = deactivate all;
        <show> exported = show (results | "active rules");

        <ruleone> exported = test rule one;
        <ruletwo> exported = test rule two;
        <rulethree> exported = test rule three;
    """
    
    def initialize(self):
        self.load(self.gramSpec)
        self.setList('rulelist', {'one', 'two', 'three'})
        self.setList('setlist', {'one', 'two'})
        self.basicset = {'show', 'activateall', 'activaterule', 'activateset',
                      'deactivateall','deactivaterule','deactivateset',
                      'activateallexcept'}
        self.activateSet(self.basicset)
        self.sets = {}
        self.sets['setone'] = {'ruleone', 'rulethree'}
        self.sets['settwo'] = {'ruletwo', 'rulethree'}
        
        self.noError = 1    # 0 (default) or 1 (print no info/error messages)

    def gotResults_ruleone(self,words,fullResults):
        print(f'\nHeard macro ruleone: "{words}"')
    def gotResults_ruletwo(self,words,fullResults):
        print(f'\nHeard macro ruletwo: "{words}"')
    def gotResults_rulethree(self,words,fullResults):
        print(f'\nHeard macro rulethree: "{words}"')
    
    def gotResults_activaterule(self,words,fullResults):
        print(f'Heard macro activaterule "{words}"')
        rulename = "rule" + words[-1]
        self.activate(rulename, noError=self.noError)
        self.show()

    def gotResults_activateset(self,words,fullResults):
        print(f'Heard macro activateset: "{words}"')
        setname = "set" + words[-1]
        self.activateSet(self.sets[setname].union(self.basicset))
        self.show()

    def gotResults_activateall(self,words,fullResults):
        print(f'Heard macro activateall: "{words}"')
        self.activateAll()
        self.show()


    def gotResults_activateallexcept(self,words,fullResults):
        print(f'Heard macro activateallexcept: "{words}"')
        self.activateAll(exceptlist=['ruleone', 'ruletwo'])
        self.show()

    def gotResults_deactivaterule(self,words,fullResults):
        print(f'Heard macro deactivaterule "{words}"')
        rulename = "rule" + words[-1]
        self.deactivate(rulename, noError=self.noError)
        self.show()

    def gotResults_deactivateset(self,words,fullResults):
        print(f'Heard macro deactivateset "{words}"')
        setname = "set" + words[-1]
        self.deactivateSet(self.sets[setname])
        self.show()
        
    def gotResults_deactivateall(self,words,fullResults):
        print(f'Heard macro deactivateall: "{words}"')
        self.deactivateAll()
        print(f'all deactivated? {self.activeRules}')
        self.activateSet(self.basicset)
        print('now the basicset is set again')
        self.show()
        
    def gotResults_show(self,words,fullResults):
        print(f'Heard macro show: "{words}"')
        print(f'activeRules: {self.activeRules}')
        active_keys = set(self.activeRules.keys())
        test_keys = active_keys - self.basicset
        print(f'test rules that are active: {test_keys}')
    
    def show(self):
        """show the results
        either with the command "show results" or after one
        of the other commands
        """
        activedict = copy.copy(self.activeRules)
        for rule in self.basicset:
            if rule not in activedict:
                print(f'basicrule {rule} NOT in activeRules')
            else:
                del activedict[rule]
        print(f'active testrules: {list(activedict.keys())}')
        
        
        
thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    #pylint:disable=W0603
    global thisGrammar
    if thisGrammar:
        thisGrammar.unload()
    thisGrammar = None
