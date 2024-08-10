#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# _sample_move_natlinktimer.py
#   Sample macro file which implements keyboard movement modes
#   similar to DragonDictate for Windows
#
# This uses a module natlinktimer (in natlinkcore).
#
# Start with: "start moving (up | down | left | right)
# Change direction and/or speed with "up faster", "down much slowere" etc.
# Stop with "stop" or by turning the microphone off.
#
# April 2022, adapting a little for python3
# August 2024, try the new natlinktimer module, only for moving (QH, August 24)
#pylint:disable= C0206, E1101, R1730, R1731
import time     
import natlink
from natlinkcore.natlinkutils import *
from natlinkcore import natlinktimer

# For caret movement, this represents the default speed in milliseconds
# between arrow keys

defaultMoveSpeed = 250

# For caret movement, this is the rate change applied when you make it
# faster.  For example, 1.5 is a 50% speed increase.

moveRateChange = 2.0


############################################################################
#
# Here are some of our instance variables
#
#   self.haveCallback   set when the timer callback in installed
#   self.curMode        1 for caret movement, or None
#   self.curSpeed       current movement speed (milliseconds for timer)
#   self.lastClock      time of last timer callback or 0
#   self.curDirection   direction of movement as string
#


class ThisGrammar(GrammarBase):

    # when we unload the grammar, we must make sure we clear the timer
    # callback so we keep a variable which is set when we currently own
    # the timer callback

    def __init__(self):
        self.haveCallback = 0
        self.curMode = None
        self.iconState = 0
        GrammarBase.__init__(self)

    def unload(self):
        # if self.haveCallback: 
        #     # natlinktimer.setTimerCallback(testGram.doTimerClassic, interval=testGram.interval, callAtMicOff=testGram.cancelMode, debug=debug)
        #     natlink.setTimerCallback(None,0)
        #     self.haveCallback = 0
        GrammarBase.unload(self)

    # This is our grammar.  The rule 'start' is what is normally active.  The
    # rules 'nowMoving' and 'nowMousing' are used when we are in caret or
    # mouse movement mode.

    gramDefn = """
        # this is the rule which is normally active
        <start> exported = <startMoving>;

        # this rule is active when we are moving the caret
        <nowMoving> exported =
            [ move ] ( {direction} | steady | fast | slow | [much] faster | [much] slower ) |
            stop [ moving ];

        # here are the subrules which deal with caret movement
        <startMoving> = start moving {direction};

    """

    # These are the lists   which we use in our grammar.  The directions and 
    # counts are implemented as lists to make parsing easier (words from
    # lists are referenced as part of the rule which includes the list).

    listDefn = {
        'direction' : ['up','down','left','right'],
        }

    # Load the grammar, build the direction and count lists and activate the
    # main rule ('start')
    
    def initialize(self):
        self.load(self.gramDefn)
        for listName in self.listDefn:
            self.setList(listName,self.listDefn[listName])
        self.activateSet(['start'],exclusive=0)

    # This subroutine cancels any active movement mode
    
    def cancelMode(self):
        self.curMode = None
        if self.haveCallback: 
            natlink.setTimerCallback(None,0)
            self.haveCallback = 0
        self.activateSet(['start'],exclusive=0)
        # natlink.setTrayIcon()

    # This function is called on a timer event.  If we are in a movement
    # mode then we move the mouse or caret by the indicated amount.
    #
    # The apparent speed for mouse movement is the speed divided by the
    # number of pixels per move.  We calculate the number of pixels per
    # move to ensure that the speed is never faster than 50 milliseconds.

    def onTimer(self):
        if self.lastClock:
            diff = int( (time.time() - self.lastClock) * 1000 )
            self.lastClock = time.time()
        if self.curMode == 1:
            moduleInfo = natlink.getCurrentModule()
            if natlink.getMicState() == 'on' and moduleInfo == self.moduleInfo:
                # self.setTrayIcon(1)
                # Note: it is often during a playString operation that the
                # "stop moving" command occurs
                natlink.playString('{'+self.curDirection+'}')
            else:
                self.cancelMode()
                
    # This handles the startMoving rule.  We only need to extract the
    # direction.  To turn on cursor movement mode we need to install a 
    # timer callback (warning: this is global) and set the recognition
    # state to be exclusively from the rule <nowMoving>.  The cursor only
    # moves in the timer callback itself.

    def gotResults_startMoving(self,words,fullResults):
        self.cancelMode()
        direction = findKeyWord(words,self.listDefn['direction'])
        self.curMode = 1
        self.curDirection = direction
        # self.setTrayIcon(0)
        self.moduleInfo = natlink.getCurrentModule()
        self.curSpeed = defaultMoveSpeed
        self.lastClock = time.time()
        self.timer = natlinktimer.createGrammarTimer(self.onTimer, self.curSpeed, callAtMicOff=self.cancelMode)
        self.timer.start()
        # print(f'started timer: {self.timer} with interval ')
        self.haveCallback = 1
        self.activateSet(['nowMoving'],exclusive=1)

    # This handles the nowMoving rule.  We want to extract the keyword which
    # tells us what to do.

    def gotResults_nowMoving(self,words,fullResults):
        direction = findKeyWord(words,self.listDefn['direction'])
        if direction:
            print(f'change direction to {direction}')
            self.curDirection = direction
            self.timer.start()
            # self.setTrayIcon(0)
        if 'stop' in words:
            self.cancelMode()
            return
        
        speed = self.curSpeed
        if 'normal' in words or 'steady' in words:
            speed = defaultMoveSpeed
        elif 'fast' in words:
            speed = int(defaultMoveSpeed / moveRateChange)
        elif 'slow' in words:
            speed = int(defaultMoveSpeed * moveRateChange)
        elif 'faster' in words:
            speed = int(self.curSpeed / moveRateChange)
            if 'much' in words:
                speed = int(speed / moveRateChange)
            if speed < 50:
                speed = 50
        elif 'slower' in words:
            speed = int(self.curSpeed * moveRateChange)
            if 'much' in words:
                speed = int(speed * moveRateChange)
            if speed > 4000:
                speed = 4000
                
                
        if self.curSpeed == speed:
            return
        self.curSpeed = speed
        self.timer.start(self.curSpeed)

    # # This turns on the tray icon depending on the movement direction.
    # # self.iconState is used to toggle the image to animate the icon.            
    # def setTrayIcon(self,toggleIcon):
    #     iconName = self.curDirection
    #     toolTip = 'moving '+self.curDirection
    #     if not toggleIcon or self.iconState:
    #         self.iconState = 0
    #     else:
    #         self.iconState = 1
    #         iconName = iconName + '2'
    #     # natlink.setTrayIcon(iconName,toolTip,self.onTrayIcon)

    # This is called if the user clicks on the tray icon.  We simply cancel
    # movement in all cases.
    # def onTrayIcon(self,message):
    #     self.cancelMode()

# This is a simple utility subroutine.  It takes two lists of words and 
# returns the first word it finds which is in both lists.  We use this to
# extract special words (like the direction) from recognition results.

def findKeyWord(list1,list2):
    for word in list1:
        if word in list2: 
            return word
    return None

#
# Here is the initialization and termination code.  See wordpad.py for more
# comments.
#

thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    #pylint:disable=W0603
    global thisGrammar
    if thisGrammar:
        thisGrammar.unload()
    thisGrammar = None

