"""
code to help with debugging including:
- enable python debuggers to attach.
currently on DAP debuggers are supported.
https://microsoft.github.io/debug-adapter-protocol/
There are several, Microsoft Visual Studio COde is known to work.
There are several, Microsoft Visual Studio COde is known to work.

If you know how to add support for another debugger please add it.

Written by Doug Ransom, 2021
"""
#pylint:disable=C0116, W0703
import os
import debugpy
from natlinkcore import natlinkstatus
import logging

__status = natlinkstatus.NatlinkStatus()
__natLinkPythonDebugPortEnviornmentVar= "NatlinkPyDebugPort"
__natLinkPythonDebugOnStartupVar="NatlinkPyDebugStartup"

__pyDefaultPythonExecutor = "python.exe"
__debug_started=False
default_debugpy_port=7474
__debugpy_debug_port=default_debugpy_port
__debugger="not configured"
dap="DAP"

#bring a couple functions from DAP and export from our namespace
dap_is_client_connected=debugpy.is_client_connected
dap_breakpoint = debugpy.breakpoint

def dap_info():
    return f"""
Debugger: {__debugger}  DAP Port:{__debugpy_debug_port} IsClientConnected: {dap_is_client_connected()} Default DAP Port {default_debugpy_port} 
Debug Started:{__debug_started}
"""

def start_dap(waitForAttach : bool =False):
    #pylint:disable=W0603
    global  __debug_started,__debugpy_debug_port,__debugger

    logging.debug("starting DAP, waitForAttach={waitForAttach}")
    if __debug_started:
        logging.debug(f"DAP already started with debugpy for port {__debugpy_debug_port}")
        return
    try:

        logging.debug(f"Starting debugpy on port {__debugpy_debug_port}")

        python_exec =  __pyDefaultPythonExecutor  #for now, only the python in system path can be used for natlink and this module
        logging.debug(f"Python Executable (required for debugging): '{python_exec}'")
        debugpy.configure(python=f"{python_exec}")
        debugpy.listen(__debugpy_debug_port)
        print(f"debugpy listening on port {__debugpy_debug_port}")
        __debug_started = True
        __debugger = dap

        if waitForAttach:
            #use logging level info, as we want this to always be shown, as the program will hang here if the debugger is not attached.
            logging.info(f"Waiting for DAP debugger to attach now")
            debugpy.wait_for_client()


    except Exception as ee:
        print(f"""
    Exception {ee} while starting debug.  Possible cause is incorrect python executable specified {python_exec}
"""     )
_debugging_docs="https://dictation-toolbox.github.io/natlink/#/debugging"

def debug_check_on_startup():
    
    logging.debug( "Instructions for attaching a python debugger are in the Natlink developer documentation: %s" % _debugging_docs)

    #pylint:disable=W0603
    global  __debug_started,__debugpy_debug_port,__debugger
    global __status
    try:
            __status = natlinkstatus.NatlinkStatus()
            __debugpy_debug_port = __status.dap_port
            dap_wait_for_attach=__status.dap_wait_for_debugger_attach_on_startup
            dap_enabled = __status.dap_enabled


    except  Exception as e:
        logging.warning("\nChecking DAP settings in {__file__} during startup, traceback:\n{e}")

    if dap_enabled:
        start_dap(dap_wait_for_attach)

    






