"""unittestNatlinktimer

Python Macro Language for Dragon NaturallySpeaking
  (c) Copyright 1999 by Joel Gould
  Portions (c) Copyright 1999 by Dragon Systems, Inc.

unittestNatlinktimer.py

  This script performs tests of the Natlinktimer module
  natlinktimer.py, for multiplexing timer instances acrross different grammars
  Quintijn Hoogenboom, summer 2020
""" 
#pylint:disable=C0115, C0116
#pylint:disable=E1101

# import sys
import time
from pathlib import Path
import pytest
import natlink
from natlinkcore.natlinkutils import GrammarBase
from natlinkcore import natlinktimer

# try some experiments more times, because gotBegin sometimes seems
# not to hit
nTries = 10
natconnectOption = 1 # or 1 for threading, 0 for not. Seems to make difference
                     # with spurious error (if set to 1), missing gotBegin and all that...

thisDir = Path(__file__).parent

# define TestError, and mark is to be NOT a part of pytest:
class TestError(Exception):
    pass
TestError.__test__ = False

# make a TestGrammar, which can be called for different instances
class TestGrammar(GrammarBase):
    def __init__(self, name="testGrammar"):
        GrammarBase.__init__(self)
        self.name = name
        self.resetExperiment()

    def resetExperiment(self):
        self.Hit = 0
        self.MaxHit = 5
        self.sleepTime = 0 # to be specified by calling instance, the sleeping time after each hit
        self.results = []

    # def __del__(self):
    #     """try to remove the grammarTimer first"""
    #     del self.grammarTimer

    def doTimer(self):
        self.results.append(f'doTimer {self.name}: {self.Hit}')
        self.Hit +=1
        time.sleep(self.sleepTime/1000)  # sleep 10 milliseconds
        if self.Hit == self.MaxHit:
            expectElapsed = self.Hit * self.interval
            print(f'expect duration of this timer: {expectElapsed} milliseconds')
            natlinktimer.removeTimerCallback(self.doTimer)
        ## try to shorten interval:
        currentInterval = self.grammarTimer.interval
        if currentInterval > 250:
            newInterval = currentInterval - 25
            return newInterval
        return None
TestGrammar.__test__ = False

    
# def testSingleTimer():
#     try:
#         natlink.natConnect()
#         testGram = TestGrammar(name="single")
#         testGram.interval = 200  # all milliseconds
#         testGram.sleepTime = 30
#         assert natlinktimer.getNatlinktimerStatus() in (0, None) 
#         cycles = 2
#         for cycle in range(cycles):
#             print(f'cycle: {cycle} of {cycles} (test is {testGram.name})')
#             testGram.resetExperiment()
#             testGram.grammarTimer = natlinktimer.setTimerCallback(testGram.doTimer, interval=testGram.interval) ##, debug=1)
#             assert natlinktimer.getNatlinktimerStatus() == 1
#             for _ in range(5):
#                 if testGram.Hit >= testGram.MaxHit:
#                     break
#                 wait(1000)   # 1 second
#             else:
#                 raise TestError('not enough time to finish the testing procedure')
#             print(f'testGram.results: {testGram.results}')
#             assert len(testGram.results) == testGram.MaxHit
#     
#             assert natlinktimer.getNatlinktimerStatus() == 0    ## natlinktimer is NOT destroyed after last timer is gone. 
# 
#     finally:
#         natlink.natDisconnect()
#     
# def testWrongValuesTimer():
#     try:
#         natlink.natConnect()
#         testGram = TestGrammar(name="wrongvalues")
#         testGram.interval = -200  # all milliseconds
#         testGram.sleepTime = 30
#         assert natlinktimer.getNatlinktimerStatus() in (0, None)
#         # testGram.resetExperiment()
#         assert testGram.Hit == 0
#         testGram.grammarTimer = natlinktimer.setTimerCallback(testGram.doTimer, interval=testGram.interval) ##, debug=1)
#         assert natlinktimer.getNatlinktimerStatus() == 0
# 
#     finally:
#         natlink.natDisconnect()

def testTwoTimers():
    try:
        natlink.natConnect()
        testGramOne = TestGrammar(name="timer_one")
        testGramOne.interval = 100  # all milliseconds
        testGramOne.sleepTime = 30
        testGramTwo = TestGrammar(name="timer_two")
        testGramTwo.interval = 77  # all milliseconds
        testGramTwo.sleepTime = 10
        assert natlinktimer.getNatlinktimerStatus() in (0, None)
        testGramOne.grammarTimer = natlinktimer.setTimerCallback(testGramOne.doTimer, interval=testGramOne.interval) ##, debug=1)
        testGramTwo.grammarTimer = natlinktimer.setTimerCallback(testGramTwo.doTimer, interval=testGramTwo.interval) ##, debug=1)
        assert natlinktimer.getNatlinktimerStatus() == 2
        for _ in range(5):
            if testGramOne.Hit >= testGramOne.MaxHit and testGramTwo.Hit >= testGramTwo.MaxHit:
                break
            wait(1000)   # 1 second
        else:
            raise TestError('not enough time to finish the testing procedure')
        print(f'testGramOne.results: {testGramOne.results}')
        print(f'testGramTwo.results: {testGramTwo.results}')
        assert len(testGramOne.results) == testGramOne.MaxHit
        assert len(testGramTwo.results) == testGramTwo.MaxHit

        assert natlinktimer.getNatlinktimerStatus() == 0    ## natlinktimer is NOT destroyed after last timer is gone. 





    finally:
        natlink.natDisconnect()
    
    
    
    
    
def wait(tmilli=100):
    """wait milliseconds via waitForSpeech loop of natlink
    
    default 100 milliseconds, or 0.1 second
    """
    tmilli = int(tmilli)
    natlink.waitForSpeech(tmilli)

if __name__ == "__main__":
    pytest.main(['test_natlinktimer.py'])
    