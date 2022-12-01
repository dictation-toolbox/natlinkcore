
# Natlinkcore 

## More Information
 Please refer to the README file in the project repository [https://github.com/dictation-toolbox/natlink](https://github.com/dictation-toolbox/natlink) for more information about natlink.

## Installing from PyPi
You can install from [The Python Package Index (PyPI)](https://pypi.org/) with 

`py -m pip install natlinkcore`

 
## Test Framework
Tests use the [pytest](https://docs.pytest.org/) framework.  
For developers, if you are developing on the project, please add tests for any new features or bug
fixes.  

Mandy Python IDEs such as [Visual Studio Code](https://code.visualstudio.com/) have build in support for test frameworks and make it easy to run and debug pytest.   see [Visual Studio Code for testing](https://code.visualstudio.com/docs/python/testing).


## Building the Python Package Locally

The build happens through a powershell script.  You don't have to know much powershell.  
The powershell script runs the tests using [pytest](https://docs.pytest.org/).  

The package is built with [Flit](https://flit.pypa.io/).  The package will be produced in
dist/natlinkcore-x.y.z-py3-none-any.whl.  To install it `py -m pip install dist/natlinkcore-x.y.z-py3-none-any.whl` replacing x.y with the version numbers.

Normally if you are developing natlinkcore, you will with instead to install with `py -m pip install -e .`, which will
let you make and test changes without reinstalling natlinkcore with pip.  **Note the flit install --symlink or --pth-file options are problematic so just use pip.**


To start a powershell from the command prompt, type `powershell`.

To build the package:


`py -m flit build`   from powershell or command prompt, which will run the the tests in natlinkcore/test, then build the the package.


To publish the package to [The Python Package Index (PyPI)](https://pypi.org/)

`publish_natlinkcore` from powershell.


 


## Publishing checklist
Before you bump the version number in __init__.py and publish:
- Check the pyroject.toml file for package dependancies.  Do you need a specfic or newer version of
a dependancy such as dtactions?  Then add or update the version # requirement in dtactions.  
- don't publish if the tests are failing.   The `publish_natlinkcore` will prevent this, please don't work around it.

## Debugging Instructions

Read the detailed developer instructions for setting up the debugger.  You can look in this projects tree until 
documentation/developers.rst.

