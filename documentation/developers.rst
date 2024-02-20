Developers instructions
=======================

Python modules
------------------

The python modules of Natlink are in a separate project 'natlinkcore'. Documentation of these modules will be developed ASAP.

The inno setup program ensures, the different projects 'natlink' (C++ code and inno setup program) and 'natlinkcore' (the core python modules) are installed in one stroke.


Compiling Natlink
------------------

The 'glue' file between python code and 'Dragon', the heart if the 'Natlink' project is a `.pyd` file, which needs to be compiled from C++ code. With this compile step, also the 'inno setup program' is compiled.

When you want to contribute to python packages, look into the instructions there...

When you want to contribute to the Natlink development, you will need to compile the C++ code and compile the inno setup program. Try the instructions below.

Setup Visual Studio Code environment
------------------------------------

1. Install `Visual Studio <https://visualstudio.microsoft.com/>`__
   (Community Edition 2019 or above) with ``C++ Desktop Development``
   and ``Microsoft Visual C++ Redistributable``.

   -  `C++ Desktop
      Development <https://docs.microsoft.com/en-us/cpp/ide/using-the-visual-studio-ide-for-cpp-desktop-development>`__
      This contains the necessary compilers for **(Visual Studio** and
      **Visual Studio Code)**
   -  `Microsoft Visual C++ Redistributable 2015, 2017, 2019, and
      2022 <https://docs.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist?view=msvc-170>`__
      (32-bit/X86 required)

2. Install `Visual Studio Code <https://visualstudio.microsoft.com/>`__
   with the following Extensions

   -  `C/C++ <https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools>`__
   -  `CMake <https://marketplace.visualstudio.com/items?itemName=twxs.cmake>`__

3. Install `Inno <https://jrsoftware.org/isdl.php>`__ version 6.x.
4. Install `Python <https://www.python.org/downloads/>`__ version 3.8.x,
   3.9.x, or 3.10.x 32-bit/X86 (Does not need to be on path)
5. After cloning Nalink open the project up in Visual Studio Code

   -  Set the Python Version ``PYTHON_VERSION 3.10`` in
      `CMakeLists.txt <https://github.com/dictation-toolbox/natlink/blob/23b40fe23c0cb75c935cae6bc6800fa9cda748d9/CMakeLists.txt#L5>`__
      (The CMakeLists.txt in top directory of the project)

      -  example for Python 3.8.x
         ``set(PYTHON_VERSION 3.8 CACHE STRING "3.X for X >= 8")``

   -  Selective equivalent to
      ``Visual Studio Community 2022 Release - x86`` (32-bit/X86
      required) to configure the compiler.

      -  |image1|

6. The ``build`` directory will generate containing the configuration
   selected and build artifacts (compiled code and installer)

   -  The ``build`` directory can be safely deleted if you need to
      reconfigure the project as it will just regenerate.

7. Click the "build" button at the bottom of the editor to to build the
   project and create the installer.

   -  |image2|
   -  ``build`` directory Installer location
      ``{project source directory}\build\InstallerSource\natlink5.1-py3.10-32-setup.exe``

.. |image1| image:: https://user-images.githubusercontent.com/24551569/164927468-68f101a5-9eed-4568-b251-0d09fde0394c.png
.. |image2| image:: https://user-images.githubusercontent.com/24551569/164919729-bd4b2096-6af3-4307-ba3c-ef6ff3b98c41.png

Debugging Natlink Python Code
------------------
Developers can debug their python natlink grammars or any
other Python code running in natlink using a debugger supporting 
`Debug Adapter Protocol: https://microsoft.github.io/debug-adapter-protocol/`_ (DAP).  

Visual Studio Code TIPS 
------------------
Create a workspace for all the projects you might want to debug in your session.
Consider making a folder like "dt" and git cloning all the projects you locally develop underneath it.

Install each python package as local editable installs 
https://pip.pypa.io/en/stable/topics/local-project-installs/ with pip.

For example, to install dragonfly and unimacro, and you are in the terminal at the "dt" root mentioned above
to install dragonfly, and unimacro (along wit the dependencies for developing and testing) from a dt directory with dragonfly: 
```pip install -e ./dragonfly
   pip install -e ./unimacro[dev,test]
```
or to install a package like dragonfly or unimacro from the git clone folder:
pip install -e .


For example, most developers will want natlink, natlinkcore, and dtactions in their workspace.
Add in dragonfly, unimacro etc. as appropriate.

It is also a good idea to add your .natlink folder into your workspace.  Then you can always quickly find your natlink.ini.



To enable DAP, add or edit your  natlink.ini to include this section.  Change the port if you need to.
::
   [settings.debugadapterprotocol]

   dap_enabled = True
   dap_port = 7474
   dap_wait_for_debugger_attach_on_startup = True

You can `check if your favorite debugger supports DAP https://microsoft.github.io/debug-adapter-protocol/implementors/tools/.  Here are instructions for Visual
Studio Code`_:  

Here is the Visual Studio code page on debugging with Python:  https://code.visualstudio.com/docs/python/debugging

Create a launch configuration in one of the projects, where you plan to set a breakpoint, for Python debugger and 
default type of Remote Attach. 

dap_enabled is usually false.  When DAP is enabled, someone with access to your computer via a LAN or open internet port
can attach a debugger to your dragon process.  If you are in a LAN environment like a corporation or university, 
you might look into disallowing access to the dap_port with a firewall, if you are using debugging features on your 
workstation.

In Natlink.ini, check that dap_enabled=True:

[settings.debugadapterprotocol]
dap_enabled = True
dap_port = 7474
dap_wait_for_debugger_attach_on_startup = False

If you change natlink.ini, restart Dragon.


Here is a sample launch.json, which you can copy into one if your Python projects .vscode folder (i.e. unimacro/.vscode).  


It is super important the pathMappings are as shown.  If you want to try remote debugging, you can explore pointing
remoteRoot to the source code on another computer.  You can also explore using SSH for remote debugging https://code.visualstudio.com/docs/remote/ssh.
If you have any sucess with those, please update this documentation.

{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debugger: Natlink Remote Attach",
            "type": "debugpy",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 7474
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "${workspaceFolder}"
                }
            ]
        }
    ]
}


Add this section to launch.json, ensuring the port number matchines natlink.ini.  Default port is 7474 
but users can change it.


 and noting
the pathMappings have been commented out:
::
        {
            "name": "Natlink: Remote Attach",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 7474
            },
            //DO NOT USE THE VISUAL STUDIO DEFAULTS
            //FOR pathMappings.
            //The defaults will not work and your breakpoints
            //will never hit.  So delete the pathMappings
            //section for local host debugging, or set them to 
            //something meaningful.  
            // "pathMappings": [
            //     {
            //         "localRoot": "${workspaceFolder}",
            //         "remoteRoot": "."
            //     }

            //a good idea to set justMyCode to false.  Otherwise
            //you may have breakpoints set that won't trigger.
            "justMyCode": false
        }


Further instructions
--------------------




Invalid options Visual Studio
-----------------------------

When the C++ compile redistributale is wrongly configured, the program `dumpbinx.exe` reports a dependency, which is not wanted:

::

  PS C:\dt\NatlinkDoc\natlink\documentation> ."C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.29.30133\bin\Hostx86\x86\dumpbin.exe" /DEPENDENTS "C:\Program Files (x86)\Natlink\site-packages\natlink\_natlink_core.pyd"
  Microsoft (R) COFF/PE Dumper Version 14.29.30136.0
  Copyright (C) Microsoft Corporation.  All rights reserved.
  
  
  Dump of file C:\Program Files (x86)\Natlink\site-packages\natlink\_natlink_core.pyd
  
  File Type: DLL
  
    Image has the following dependencies:
  
      python38.dll
      KERNEL32.dll
      USER32.dll
      SHELL32.dll
      ole32.dll
      OLEAUT32.dll
      ADVAPI32.dll
      MSVCP140D.dll
      VCRUNTIME140D.dll
      ucrtbased.dll
      
  (...)

The `VCRUNTIME140D.dll` should not be there.

Fix
---

Static linking is established by installing:
https://docs.microsoft.com/en-us/cpp/c-runtime-library/crt-library-features?view=msvc-170&viewFallbackFrom=vs-2019

Also see "Bundling vc redistributables":
https://stackoverflow.com/questions/24574035/how-to-install-microsoft-vc-redistributables-silently-in-inno-setup


With install version 5.1.1  (with python 3.8), now the following output is given:

::

  (Powershell) ."C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.29.30133\bin\Hostx86\x86\dumpbin.exe" /DEPENDENTS "C:\Program Files (x86)\Natlink\site-packages\natlink\_natlink_core.pyd"
  Dump of file C:\Program Files (x86)\Natlink\site-packages\natlink\_natlink_core.pyd
  
  File Type: DLL
  
    Image has the following dependencies:
  
      python38.dll
      KERNEL32.dll
      USER32.dll
      SHELL32.dll
      ole32.dll
      OLEAUT32.dll
      ADVAPI32.dll
  (...)


So issue#86(https://github.com/dictation-toolbox/natlink/issues/86) is hopefully solved and explained with this all.


.. _issue#86: https://github.com/dictation-toolbox/natlink/issues/86

