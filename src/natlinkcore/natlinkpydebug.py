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

__status = natlinkstatus.NatlinkStatus()
__natLinkPythonDebugPortEnviornmentVar= "NatlinkPyDebugPort"
__natLinkPythonDebugOnStartupVar="NatlinkPyDebugStartup"

__pyDefaultPythonExecutor = "python.exe"
__debug_started=False
__debugpy_debug_port=0
__debugger="not configured"
dap="DAP"

#bring a couple functions from DAP and export from our namespace
dap_is_client_connected=debugpy.is_client_connected
dap_breakpoint = debugpy.breakpoint

def dap_info():
    return f"""
Debugger: {__debugger}  DAP Port:{__debugpy_debug_port} IsClientConnected: {dap_is_client_connected()}  
Debug Started:{__debug_started}
"""

def start_dap(debugpy_port, wait_now_for_debugger_attach):
    #pylint:disable=W0603
    global  __debug_started,__debugpy_debug_port,__debugger
    if __debug_started:
        print(f"DAP already started with debugpy for port {debugpy_port}")
        return
    try:

        __debugpy_debug_port = int(natLinkPythonPortStringVal)
        print(f"Starting debugpy on port {natLinkPythonPortStringVal}")

        python_exec =  __pyDefaultPythonExecutor  #for now, only the python in system path can be used for natlink and this module
        print(f"Python Executable (required for debugging): '{python_exec}'")
        debugpy.configure(python=f"{python_exec}")
        debugpy.listen(debugpy_port)
        print(f"debugpy listening on port {__debugpy_debug_port}")
        __debug_started = True
        __debugger = dap


        if wait_now_for_debugger_attach:
            print(f"Waiting for DAP debugger to attach ")
            debugpy.wait_for_client()


    except Exception as ee:
        print(f"""
    Exception {ee} while starting debug.  Possible cause is incorrect python executable specified {python_exec}
"""     )

def debug_check_on_startup():
    #pylint:disable=W0603
    global  __debug_started,__debugpy_debug_port,__debugger
    debug_instructions = f"{__status.getCoreDirectory()}\\debugging python instructions.docx"
    print(f"Instructions for attaching a python debugger are in {debug_instructions} ")
    if __natLinkPythonDebugPortEnviornmentVar in os.environ:
        start_dap()






