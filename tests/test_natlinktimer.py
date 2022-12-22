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

thisDir = Path(__file__).parent

# define TestError, and mark is to be NOT a part of pytest:
class TestError(Exception):
    pass
TestError.__test__ = False

debug = 1

# make a TestGrammar, which can be called for different instances
class TestGrammar(GrammarBase):
    def __init__(self, name="testGrammar"):
        GrammarBase.__init__(self)
        self.name = name
        self.resetExperiment()

    def resetExperiment(self):
        self.Hit = 0
        self.MaxHit = 5
        self.toggleMicAt = None
        self.sleepTime = 0 # to be specified by calling instance, the sleeping time after each hit
        self.results = []
        self.starttime = round(time.time()*1000)
        self.startCancelMode = False
        self.endCancelMode = False

    def cancelMode(self):
        """timer should stop, and the 2 instance variables set to True
        """
        self.startCancelMode = True
        natlinktimer.setTimerCallback(self.doTimerClassic,0)
        self.endCancelMode = True

    def doTimerClassic(self):
        """have no introspection, but be as close as possible to the old calling method of setTimerCallback
        
        """
        now = round(time.time()*1000)
        relTime = now - self.starttime
        self.results.append(f'{self.Hit} {self.name}: {relTime}')
        self.Hit +=1
        if self.Hit:
            if self.toggleMicAt and self.toggleMicAt == self.Hit:
                ## run the on_mic_off_callback function:
                natlinktimer.natlinktimer.on_mic_off_callback()
            # decrease the interval at each step. There should be
            # a bottom, depending on the time the routine is taking (eg minimal 3 times the time the callback takes).
            # this is tested by setting the sleeptime
            self.interval -= 10
            if self.sleepTime:
                time.sleep(self.sleepTime/1000) 
            natlinktimer.setTimerCallback(self.doTimerClassic, interval=self.interval, callAtMicOff=self.cancelMode)
            
        # time.sleep(self.sleepTime/1000)  # sleep 10 milliseconds
        if self.Hit == self.MaxHit:
            natlinktimer.setTimerCallback(self.doTimerClassic, 0)

    def doTimer(self):
        """the doTimer function can remove itself, return None or another interval
        
        """
        relTime = round(time.time()*1000) - self.starttime
        self.results.append(f'{self.Hit} {self.name} ({self.grammarTimer.interval}): {relTime}')
        self.Hit +=1
        time.sleep(self.sleepTime/1000)  # sleep 10 milliseconds
        if self.Hit == self.MaxHit:
            expectElapsed = self.Hit * self.interval
            print(f'expect duration of timer {self.name}: {expectElapsed} milliseconds')
            natlinktimer.removeTimerCallback(self.doTimer)
        ## try to shorten interval:
        currentInterval = self.grammarTimer.interval
        if currentInterval > 250:
            newInterval = currentInterval - 25
            return newInterval
        return None
    

        
    def toggleMicrophone(self):
        micstate = natlink.getMicState()
        if micstate == 'off':
            natlink.setMicState('on')
            time.sleep(0.1)
        natlink.setMicState('off')
    
TestGrammar.__test__ = False

    def testIcons(self):
        """in the subdirectory icons of Unimacro there are 4 icons
        
        These should show up when natlink.setTrayIcon('_repeat.ico', 'tooltip', func) is called,
        but this is not working any more.
        There are also predefined icons, which are now stored in defaulticons directory of unimacro (fork)
        
        I don't know how to call these again...
        
It was tested in C:\DT\NatlinkDoug\pythonsrc\tests\unittestNatlink.py, this test could be taken out and put into
a pytest module!
        
**From natlink.txt**:
        
setTrayIcon( iconName, toolTip, callback )
	This function, provided by Jonathan Epstein, will draw an icon in the
	tray section of the tackbar.  

	Pass in the absolute path to a Windows icon file (.ico) or pass in one
	of the following predefined names: 
		'right', 'right2', 'down', 'down2',
		'left', 'left2', 'up', 'up2', 'nodir' 
	You can also pass in an empty string (or nothing) to remove the tray
	icon.

	The toolTip parameter is optional.  It is the text which is displayed
	as a tooltip when the mouse is over the tray icon.  If missing, a generic
	tooltip is used.

	The callback parameter is optional.  When used, it should be a Python
	function which will be called when a mouse event occurs for the tray
	icon.  The function should take one parameters which is the type of
	mouse event:
		wm_lbuttondown, wm_lbuttonup, wm_lbuttondblclk, wm_rbuttondown, 
		wm_rbuttonup, wm_rbuttondblclk, wm_mbuttondown, wm_mbuttonup, 
		or wm_mbuttondblclk (all defined in natlinkutils)

	Raises ValueError if the iconName is invalid.

The following functions are used in the natlinkmain base module.  You
should only used these if you are control NatSpeak using the NatLink module
instead of using Python as a command and control subsystem for NatSpeak. In
the later case, users programs should probably not use either of these two
functions because they replace the callback used by the natlinkmain module
which could prevent proper module (re)loading and user changes.
        
        """
        natlink.setTrayIcon('_repeat.ico')
        natlink.setTrayIcon('_down')   # ????
        
        
        
# def testSingleTimerClassic():
#     try:
#         natlink.natConnect()
#         testGram = TestGrammar(name="single")
#         testGram.resetExperiment()
#         testGram.interval = 100  # all milliseconds
#         testGram.sleepTime = 20
#         testGram.MaxHit = 6
# 
#         assert natlinktimer.getNatlinktimerStatus() in (0, None) 
#         natlinktimer.setTimerCallback(testGram.doTimerClassic, interval=testGram.interval, debug=debug)
#         ## 1 timer active:
#         assert natlinktimer.getNatlinktimerStatus() == 1     
#         for _ in range(5):
#             if testGram.Hit >= testGram.MaxHit:
#                 break
#             wait(500)   # 0.5 second
#             if debug:
#                 print(f'waited 0.1 second for timer to finish testGram, Hit: {testGram.Hit} ({testGram.MaxHit})')
#         else:
#             raise TestError(f'not enough time to finish the testing procedure (came to {testGram.Hit} of {testGram.MaxHit})')
#         print(f'testGram.results: {testGram.results}')
#         assert len(testGram.results) == testGram.MaxHit
#         assert testGram.interval == 40
#         assert testGram.sleepTime == 20
#         assert natlinktimer.getNatlinktimerStatus() == 0    ## natlinktimer is NOT destroyed after last timer is gone. 
# 
#     finally:
#         del natlinktimer.natlinktimer
#         natlinktimer.stopTimerCallback()
#         natlink.natDisconnect()
        
    
def testStopAtMicOff():
    try:
        natlink.natConnect()
        testGram = TestGrammar(name="stop_at_mic_off")
        testGram.resetExperiment()
        testGram.interval = 100  # all milliseconds
        testGram.sleepTime = 20
        testGram.MaxHit = 6
        testGram.toggleMicAt = 3
        assert natlinktimer.getNatlinktimerStatus() in (0, None) 
        natlinktimer.setTimerCallback(testGram.doTimerClassic, interval=testGram.interval, callAtMicOff=testGram.cancelMode, debug=debug)
        ## 1 timer active:
        for _ in range(5):
            if testGram.toggleMicAt and testGram.Hit >= testGram.toggleMicAt:
                break
            if testGram.Hit >= testGram.MaxHit:
                break
            wait(500)   # 0.5 second
            if debug:
                print(f'waited 0.1 second for timer to finish testGram, Hit: {testGram.Hit} ({testGram.MaxHit})')
        else:
            raise TestError(f'not enough time to finish the testing procedure (came to {testGram.Hit} of {testGram.MaxHit})')
        print(f'testGram.results: {testGram.results}')
        assert len(testGram.results) == testGram.toggleMicAt
        assert natlinktimer.getNatlinktimerStatus() == 0    ## natlinktimer is NOT destroyed after last timer is gone. 
        assert testGram.startCancelMode is True
        assert testGram.endCancelMode is True

    finally:
        natlinktimer.stopTimerCallback()
        natlink.natDisconnect()
        

# def testStopAtMicOff():
#     try:
#         natlink.natConnect()
#         testGram = TestGrammar(name="single")
#         testGram.interval = 100  # all milliseconds
#         testGram.sleepTime = 20
#         testGram.MaxHit = 10
#         assert natlinktimer.getNatlinktimerStatus() in (0, None)
#         testGram.resetExperiment()
# 
#         gt = testGram.grammarTimerMicOff = natlinktimer.setTimerCallback(testGram.doTimer, interval=testGram.interval, debug=debug)
#         gtmicoff = testGram.grammarTimerMicOff = natlinktimer.setTimerCallback(testGram.doTimerMicToggle, interval=testGram.interval*3, debug=debug)
#         gtstr = str(gt)
#         gtmicoffstr = str(gtmicoff)
#         assert gtstr == 'grammartimer, interval: 100, nextTime (relative): 100'
#         assert gtmicoffstr == 'grammartimer, interval: 300, nextTime (relative): 300'
#         ## 2 timers active:
#         assert natlinktimer.getNatlinktimerStatus() == 2
#         for _ in range(5):
#             if testGram.Hit >= testGram.MaxHit:
#                 break
#             wait(1000)   # 0.1 second
#             if debug:
#                 print(f'waited 0.1 second for timer to finish testGram, Hit: {testGram.Hit} ({testGram.MaxHit})')
#         else:
#             raise TestError(f'not enough time to finish the testing procedure (came to {testGram.Hit} of {testGram.MaxHit})')
#         print(f'testGram.results: {testGram.results}')
#         assert len(testGram.results) == testGram.MaxHit
# 
#         assert natlinktimer.getNatlinktimerStatus() == 0    ## natlinktimer is NOT destroyed after last timer is gone. 
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
# 
#         
# def testThreeTimersMinimalSleepTime():
#     try:
#         if debug:
#             print('testThreeTimersMinimalSleepTime')
#         natlink.natConnect()
#         testGramOne = TestGrammar(name="min_sleeptime_one")
#         testGramOne.interval = 100  # all milliseconds
#         testGramOne.sleepTime = 2
#         testGramTwo = TestGrammar(name="min_sleeptime_two")
#         testGramTwo.interval = 50  # all milliseconds
#         testGramTwo.sleepTime = 2
#         testGramThree = TestGrammar(name="min_sleeptime_three")
#         testGramThree.interval = 100  # all milliseconds
#         testGramThree.sleepTime = 2
#         testGramThree.MaxHit = 2
#         assert natlinktimer.getNatlinktimerStatus() in (0, None)
#         testGramOne.grammarTimer = natlinktimer.setTimerCallback(testGramOne.doTimer, interval=testGramOne.interval, debug=debug)
#         testGramTwo.grammarTimer = natlinktimer.setTimerCallback(testGramTwo.doTimer, interval=testGramTwo.interval, debug=debug)
#         testGramThree.grammarTimer = natlinktimer.setTimerCallback(testGramThree.doTimer, interval=testGramThree.interval, debug=debug)
#         assert natlinktimer.getNatlinktimerStatus() == 3
#         for _ in range(5):
#             if testGramOne.Hit >= testGramOne.MaxHit and testGramTwo.Hit >= testGramTwo.MaxHit:
#                 break
#             wait(1000)   # 1 second
#         else:
#             raise TestError('not enough time to finish the testing procedure')
#         print(f'testGramOne.results: {testGramOne.results}')
#         print(f'testGramTwo.results: {testGramTwo.results}')
#         print(f'testGramThree.results: {testGramThree.results}')
#         assert len(testGramOne.results) == testGramOne.MaxHit
#         assert len(testGramTwo.results) == testGramTwo.MaxHit
# 
#         assert natlinktimer.getNatlinktimerStatus() == 0    ## natlinktimer is NOT destroyed after last timer is gone. 
# 
#     finally:
#         natlink.natDisconnect()
#     
    

    
    
def wait(tmilli=100):
    """wait milliseconds via waitForSpeech loop of natlink
    
    default 100 milliseconds, or 0.1 second
    """
    tmilli = int(tmilli)
    natlink.waitForSpeech(tmilli)

if __name__ == "__main__":
    pytest.main(['test_natlinktimer.py'])
    