
# Natlinkcore 

## More Information
 Please refer to the README file in the project repository [https://github.com/dictation-toolbox/natlink](https://github.com/dictation-toolbox/natlink) for more information about natlink.

## Installing from PyPi
You can install from [The Python Package Index (PyPI)](https://pypi.org/) with 

`py -m pip install natlinkcore`

Note that natlinkcore will not install if you have not installed Natlink first.  Natlink is installed through running an installer.

 
## Test Framework
Tests use the [pytest](https://docs.pytest.org/) framework.  
For developers, if you are developing on the project, please add tests for any new features or bug
fixes.  

Mandy Python IDEs such as [Visual Studio Code](https://code.visualstudio.com/) have build in support for test frameworks and make it easy to run and debug pytest.   see [Visual Studio Code for testing](https://code.visualstudio.com/docs/python/testing).


## Building the Python Package Locally

`py -m build` to build the Python package locally.

Publishing to PyPi is done through the [trusted publisher mechanism](https://docs.pypi.org/trusted-publishers/using-a-publisher/) when a release is created on github using github actions. 


## Publishing checklist
Before you bump the version number in __init__.py and publish:
- Check the pyroject.toml file for package dependancies.  Do you need a specfic or newer version of
a dependancy such as dtactions?  Then add or update the version # requirement in dtactions.  

## Debugging Instructions

Read the detailed developer instructions for setting up the debugger.  You can look in this projects tree until 
documentation/developers.rst.

