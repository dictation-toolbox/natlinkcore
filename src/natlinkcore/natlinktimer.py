"""
Handling of more calls to the Natlink timer

make it a Singleton class (December 2022)
Quintijn Hoogenboom

"""
#pylint:disable=R0913

#---------------------------------------------------------------------------
import time
import traceback
import operator
import logging

import natlink
from natlinkcore import singleton, loader, config
Logger = logging.getLogger('natlink')
Config = config.NatlinkConfig.from_first_found_file(loader.config_locations())
natlinkmain = loader.NatlinkMain(Logger, Config)

## this variable will hold the (only) NatlinkTimer instance
natlinktimer = None

class GrammarTimer:
    """object which specifies how to call the natlinkTimer
    
    The function to be called when the mic switches off needs to be set only once, and is then preserved
    """
    #pylint:disable=R0913
    def __init__(self, callback, interval, callAtMicOff=False, maxIterations=None):
        curTime = self.starttime = round(time.time()*1000)
        self.callback = callback
        self.interval = interval
        
        self.nextTime = curTime +  interval
        
        self.callAtMicOff = callAtMicOff
        self.maxIterations = maxIterations

    def __str__(self):
        """make string with nextTime value relative to the starttime of the grammarTimer instance
        """
        result = f'grammartimer, interval: {self.interval}, nextTime (relative): {self.nextTime - self.starttime}'
        return result

    def __repr__(self):
        L = ['GrammarTimer instance:']
        for varname in 'interval', 'nextTime', 'callAtMicOff', 'maxIterations':
            value = self.__dict__.get(varname, None)
            if not value is None:
                L.append(f'    {varname.ljust(13)}: {value}')
        return "\n".join(L)

    def start(self, newInterval=0):
        """start (or continue), optionally with new interval
        """
        if newInterval:
            oldInterval, self.interval = self.interval, newInterval
            self.nextTime = self.nextTime - oldInterval + newInterval
        if not natlinktimer.in_timer:
            natlinktimer.hittimer()


class NatlinkTimer(metaclass=singleton.Singleton):  
    """
    This class utilises :meth:`natlink.setTimerCallback`, but multiplexes
    
    In this way, more grammars can use the single Natlink timer together.
    
    First written by Christo Butcher for Dragonfly, now enhanced by Quintijn Hoogenboom, May 2020/December 2022
    
    """
    def __init__(self, minInterval=None):
        """initialize the natlink timer instance
        
        This is singleton class, with only one instance, so more "calls" automatically connect
        to the same instance.
        
        The grammar callback functions are the keys of the self.callbacks dict,
        The corresponding values are GrammarTimer instances, which specify interval and possibly other parameters
        
        The minimum interval for the timer can be specified, is 50 by default.
        """
        self.callbacks = {}
        self.debug = False
        self.timerStartTime = self.getnow()
        self.minInterval = minInterval or 50
        self.tolerance = min(10, int(self.minInterval/4))
        self.in_timer = False
        self.timers_to_stop = set()    # will be used when a timer wants to be removed when in_timer is True
        natlinkmain.set_on_mic_off_callback(self.on_mic_off_callback)
        
    def __del__(self):
        """stop the timer, when destroyed
        """
        self.stopTimer()

    def setDebug(self, debug):
        """set debug option
        """
        if debug:
            self.debug = True
    def clearDebug(self):
        """clear debug option
        """
        self.debug = False
    
    def getnow(self):
        """get time in milliseconds
        """
        return round(time.time()*1000)

    def on_mic_off_callback(self):
        """all callbacks that have callAtMicOff set, will be stopped (and deleted)
        """
        # print('on_mic_off_callback')
        to_stop = [(cb, gt) for (cb, gt) in self.callbacks.items() if gt.callAtMicOff]
        if not to_stop:
            if self.debug:
                print('natlinktimer: no timers to stop')
            return
        for cb, gt in to_stop:
            if self.debug:
                print(f'natlinktimer: stopping {cb}, {gt}')
            gt.callAtMicOff()

    def addCallback(self, callback, interval, callAtMicOff=False, maxIterations=None, debug=None):
        """add an interval 
        """ 
        self.debug = debug
        now = self.getnow()

        if interval <= 0:
            self.removeCallback(callback)
            return None
        interval = max(round(interval), self.minInterval)
        gt = GrammarTimer(callback, interval, callAtMicOff=callAtMicOff, maxIterations=maxIterations)
        self.callbacks[callback] = gt
        if self.debug:
            print(f'set new timer {callback.__name__},  {interval} ({now})')
        
        return gt

    def removeCallback(self, callback, debug=None):
        """remove a callback function
        """
        self.debug = self.debug or debug
        if self.debug:
            print(f'remove timer for {callback.__name__}')

        if self.in_timer:
            # print(f'removeCallback, in_timer: {self.in_timer}, add {callback} to timers_to_stop')
            self.timers_to_stop.add(callback)
            return

        # outside in_timer:
        try:
            print('remove 1 timer')
            del self.callbacks[callback]
        except KeyError:
            pass
        if not self.callbacks:
            if self.debug:
                print("last timer removed, setTimerCallback to 0")

            self.stopTimer()
            return
        
        
    def hittimer(self):
        """move to a next callback point
        """
        #pylint:disable=R0914, R0912, R0915, W0702
        self.in_timer = True
        try:
            now = self.getnow()
            nowRel = now - self.timerStartTime
            if self.debug:
                print(f'start hittimer at {nowRel}')
    
            toBeRemoved = []
            # c = callbackFunc, g = grammarTimer
            # sort for shortest interval times first, only sort on interval:
            decorated = [(g.interval, c, g) for (c, g)  in self.callbacks.items()]
            sortedList = sorted(decorated, key=operator.itemgetter(0))
            
            
            for interval, callbackFunc, grammarTimer in sortedList:
                now = self.getnow()
                # for printing: 
                if self.debug:
                    nowRel, nextTimeRel = now - self.timerStartTime, grammarTimer.nextTime - self.timerStartTime
                if grammarTimer.nextTime > (now + self.tolerance):
                    if self.debug:
                        print(f'no need for {callbackFunc.__name__}, now: {nowRel}, nextTime: {nextTimeRel}')
                    continue
    
                # now treat the callback, grammarTimer.nextTime > now - tolerance:
                hitTooLate = now - grammarTimer.nextTime
                
                if self.debug:
                    print(f"do callback {callbackFunc.__name__} at {nowRel}, was expected at: {nextTimeRel}, interval: {interval}")
    
                ## now do the callback function:
                newInterval = None
                startCallback = now
                try:
                    newIntervalOrNone = callbackFunc()
                except:
                    print(f"exception in callbackFunc ({callbackFunc}), remove from list")
                    traceback.print_exc()
                    toBeRemoved.append(callbackFunc)
                    endCallback = None
                    newIntervalOrNone = None
                else:
                    endCallback = self.getnow()
                
                if newIntervalOrNone is None:
                    pass
                elif newIntervalOrNone <= 0:
                    print(f"newInterval <= 0, as result of {callbackFunc.__name__}: {newInterval}, remove the callback function")
                    toBeRemoved.append(callbackFunc)
                    continue
                
                # if cbFunc ended correct, but took too much time, its interval should be doubled:
                if endCallback is None:
                    pass
                else:
                    spentInCallback = endCallback - startCallback
                    if spentInCallback > interval:
                        if self.debug:
                            print(f"spent too much time in {callbackFunc.__name__}, increase interval from {interval} to: {spentInCallback*2}")
                        grammarTimer.interval = interval = spentInCallback*2
                    grammarTimer.nextTime += interval
                    if self.debug:
                        nextTimeRelative = grammarTimer.nextTime - endCallback
                        print(f"new nextTime: {nextTimeRelative}, interval: {interval}, from gt instance: {grammarTimer.interval}")
    
            for gt in toBeRemoved:
                del self.callbacks[gt]
            
            if not self.callbacks:
                if self.debug:
                    print("no callbackFunction any more, switch off the natlink timerCallback")
                self.stopTimer()
                return
            
            nownow = self.getnow()
            timeincallbacks = nownow - now
            if self.debug:
                print(f'time in callbacks: {timeincallbacks}')
            nextTime = min(gt.nextTime-nownow for gt in self.callbacks.values())
            if nextTime < self.minInterval:
                if self.debug:
                    print(f"warning, nextTime too small: {nextTime}, set at minimum {self.minInterval}")
                nextTime = self.minInterval
            if self.debug:
                print(f'set nextTime to: {nextTime}')
            natlink.setTimerCallback(self.hittimer, nextTime)
            if self.debug:
                nownownow = self.getnow()
                timeinclosingphase = nownownow - nownow
                totaltime = nownownow - now
                print(f"time taken in closingphase: {timeinclosingphase}")
                print(f"total time spent hittimer: {totaltime}")
        finally:
            self.in_timer = False
            if self.timers_to_stop:
                n_timers = len(self.timers_to_stop)
                if n_timers == 1:
                    print('stop 1 timer (at end of hittimer)')
                else:
                    print(f'stop {n_timers} timers (at end of hittimer)')
                for callback in self.timers_to_stop:
                    self.removeCallback(callback)
                self.timers_to_stop = set()
                
            
            
    def stopTimer(self):
        """stop the natlink timer, by passing in None, 0
        """
        natlink.setTimerCallback(None, 0)
        
def createGrammarTimer(callback, interval=0, callAtMicOff=False, maxIterations=None, debug=None):
    """return a grammarTimer instance
    
    parameters:
    callback: a function into which natlinktime will callback
    interval: a starting interval (or 0), with which the timer shall run (initially)
    optional:
    callAtMicOff: default False. When True, the timer stops when the mic is toggled to off
    maxIterations: default None. When a positive int, stop when this count is exceeded
    debug: sets the debug status for the whole natlinktimer instance, including the grammarTimer instance

    Note: the grammarTimer is NOT started, but when other timers are running it is taken in the flow.
    Call grammarTimer.start(newInterval=None) to start the timer (starting with the waiting interval) or
    grammarTimer.startNow(newInterval=None) to start immediate and then hits at each interval.
    
    Note: all intervals are in milliseconds.
    """
    #pylint:disable=W0603
    global natlinktimer
    if not natlinktimer:
        natlinktimer = NatlinkTimer()
    if debug:
        natlinktimer.setDebug(debug)
    if not natlinktimer:
        raise Exception("NatlinkTimer cannot be started")
    
    if callback is None:
        raise Exception("stop the timer callback with natlinktimer.removeCallback(callback)")
    
    if interval > 0:
        gt = natlinktimer.addCallback(callback, interval, callAtMicOff=callAtMicOff, maxIterations=maxIterations, debug=debug)
        return gt
    raise ValueError(f'Did not start grammarTimer instance {callback}, because the interval is not a positive value')
    
    
def setTimerCallback(callback, interval, callAtMicOff=None, maxIterations=None, debug=None):
    """This function sets a timercallback, nearly the same as natlink.setTimerCallback
    
    Interval in milliseconds, unless smaller than 25 (default)
    
    When 0 or negative: it functions as removeTimerCallback!!
    
    callAtMicOff: the function that will be called when the mic switches off
    
    But there are extra parameters possible, which are passed on to createGrammarTimer, see there
    
    """
    #pylint:disable=W0603
    try:
        natlinktimer
    except NameError:
        print('natlinktimer is gone')
        return
    
    if interval > 0:
        if natlinktimer and callback in natlinktimer.callbacks:
            gt = natlinktimer.callbacks[callback]
            rel_cur_time = round(time.time()*1000) - gt.starttime
            if callAtMicOff:
                gt.callAtMicOff = callAtMicOff
            if natlinktimer.debug:
                print(f'{gt}\n\ttime: {rel_cur_time}, new interval: {interval}, nextTime: {gt.nextTime-gt.starttime}')
            gt.start(newInterval=interval)
        else:
            createGrammarTimer(callback, interval, callAtMicOff=callAtMicOff, maxIterations=maxIterations, debug=debug)
            natlinktimer.hittimer()
        return 
    # interval is 0 (or negative), remove the callback
    removeTimerCallback(callback)
    return 
    

def removeTimerCallback(callback, debug=None):
    """This function removes a callback from the callbacks dict
    
    callback: the function to be called
    """
    if not natlinktimer:
        print(f'no timers active, cannot remove {callback} from natlinktimer')
        return
    
    if callback is None:
        raise Exception("please stop the timer callback with removeTimerCallback(callback)\n    or with setTimerCallback(callback, 0)")
    
    natlinktimer.removeCallback(callback, debug=debug)

def stopTimerCallback():
    """should be called at destroy of Natlink
    """
    #pylint:disable=W0603    
    global natlinktimer
    natlink.setTimerCallback(None, 0)
    try:
        del natlinktimer
    except NameError:
        pass
        
def getNatlinktimerStatus():
    """report how many callbacks are active, None if natlinktimer is gone
    """
    try:
        natlinktimer
    except NameError:
        return None
    if natlinktimer is None:
        return None
    return len(natlinktimer.callbacks)

