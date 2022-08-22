#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 2000 by Joel Gould
#   Portions (c) Copyright 2000 by Dragon Systems, Inc.
#
# demonstrate dgndication, dgnwords and dgnletters...
# Put in MacroSystem folder and toggle the microphone.
#
# this test has been augmented a bit:
#
# the rule <dgnwords>, catching only one word has been added
# optional words after the dictation have been added, in order
# to perform additional actions.
# the word "stop" is not useful, and is not caught in the <dgnletters> rule.
# the copy commands seem to function quite well!
# (Quintijn Hoogenboom, August 2022)
#
#pylint:disable=C0209
import time
import natlink
from natlinkcore.natlinkutils import *
from natlinkcore import nsformat

class ThisGrammar(GrammarBase):   

    gramSpec = """
        <dgndictation> imported;
        <dgnletters> imported;
        <dgnwords> imported;
        <ruleOne> exported = demodictate <dgndictation> [stop|<copythings>];
        <ruleTwo> exported = demospell <dgnletters> [stop|<copythings>];
        <ruleThree> exported = demooneword <dgnwords> [stop|<copythings>];
        <copythings> = copy (that|line|all);
    """
#hello


    def gotResults_dgndictation(self,words,fullResults):
        """format the words with nsformat and print.
        
        With more commands in succession, the lastState is used to fix spacing and capitalization of words.
        """
        formatted_words, self.lastState = nsformat.formatWords(words, self.lastState)
        self.lenOfWords = len(formatted_words)
        natlink.playString(formatted_words)

    def gotResults_dgnletters(self,words,fullResults):
        """the formatting is also done via nsformat
        
           but... the "commented out" trick works in practice equally well.
        """
        print(f'words for dgnletters: {words}')
        letters = nsformat.formatLetters(words)
        self.lenOfWords = len(letters)
        natlink.playString(letters)

    def gotResults_dgnwords(self,words,fullResults):
        """only catching one word of dictation
        
        """
        print(f'only one word for dgnwords: {words}')
        letters = nsformat.formatLetters(words)
        self.lenOfWords = len(letters)
        natlink.playString(letters)


    def gotResults_ruleOne(self,words,fullResults):
        """do an action if words at end of command are caught
        """
        print(f'words for ruleOne: {words}')
           
    def gotResults_ruleTwo(self,words,fullResults):
        """this is to catch the fixed words of ruleTwo
        """
        print(f'words for ruleTwo: {words}')

    def gotResults_ruleThree(self,words,fullResults):
        """this is to catch the fixed words of ruleThree
        """
        print(f'words for ruleThree: {words}')

    def gotResults_copythings(self, words, fullResults):
        """copy last, line or all
        """
        print(f'words for copythings: {words}')
        if 'line' in words:
            print('copy line!!')
            natlink.playString('{shift+home}')
        elif 'that' in words:
            natlink.playString('{shift+left %s}'% self.lenOfWords)
        elif 'all' in words:
            natlink.playString('{ctrl+a}')
        else:
            raise ValueError('options should be "line", "that" and "all"')

        if 'copy' in words:
            natlink.playString('{ctrl+c}')
            time.sleep(0.3)
        else:
            raise ValueError('word "copy" should be in words')
        
        if 'line' in words:
            natlink.playString('{end}')
        elif 'that' in words:
            print(f'go back after copy that, {self.lenOfWords} characters')
            natlink.playString('{right}')
        elif 'all' in words:
            natlink.playString('{right}')
        else:
            raise ValueError('options should be "line", "that" and "all"')           


    def initialize(self):
        self.lastState = None
        self.lenOfWords = 0
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
