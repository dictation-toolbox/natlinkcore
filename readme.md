
# Natlinkcore 

## More Information
 Please refer to the README file in the project repository [https://github.com/dictation-toolbox/natlink](https://github.com/dictation-toolbox/natlink) for more information about natlink.

## Installing from PyPi
You can install from [The Python Package Index (PyPI)](https://pypi.org/) with 

`py -m pip install natlinkcore`

Note that natlinkcore will not install if you have not installed Natlink first.  Natlink is installed through running an installer.

This will install utilties you can run from a shell prompt:  natlinkconfig_cli, natlinkconfig_gui, and natlink_extract_ini_value.

You can use natlink_extract_ini_value to grab a directory or setting out of natlink.ini for copying and pasting or a shell script.
``` 
PS C:\Users\doug\code\dt\natlinkcore> natlink_extract_ini_value -s directories -k  dragonflyuserdirectory
C:\Users\doug\Documents
```

 
## Test Framework
Tests use the [pytest](https://docs.pytest.org/) framework.  
For developers, if you are developing on the project, please add tests for any new features or bug
fixes.  

Mandy Python IDEs such as [Visual Studio Code](https://code.visualstudio.com/) have build in support for test frameworks and make it easy to run and debug pytest.   see [Visual Studio Code for testing](https://code.visualstudio.com/docs/python/testing).


## Building the Python Package Locally

`py -m build` to build the Python package locally.

Publishing to PyPi is done through the [trusted publisher mechanism](https://docs.pypi.org/trusted-publishers/using-a-publisher/) when a release is created on github using github actions. 


## Version Numbering and Publishing Checklist

While you are developing, use a .dev release number.  When you are ready for alpha or beta or release candidate, use the appropriate version numbers.
If you are submitting a pull request, the review should review and adjust the version number.  
The version specificier is in pyroject.toml.


The version number progression is explained in [PEP440](https://peps.python.org/pep-0440/#summary-of-permitted-suffixes-and-relative-ordering).  

Hypothetical Progression of release numbers.  

Working towards 5.4.0:
- 5.4.0.dev1
- 5.4.0.dev2
- 5.4.0.dev_feature_x
- 5.4.0a1
- 5.4.0b1dev1
- 5.4.0b1
- 5.4.0rc1
- 5.4.0rc2
- 5.4.0

Use alpha and beta specifiers (5.4a2, 5.4.b1, etc) to release alphas and betas.
If you go through a release candidate phase, use 5.4rc1 etc.

Non breaking changes, add a micro version number.  ie from version 5.4.1 to 5.4.2.
Breaking changes, add a minor version number.

*Before you publish to pypi*:
- doublecheck the dependancies, especially on natlink.  You may want to specify a minimum natlink (i.e. 5.5.3) and 
normally you should also specify that natlink has not had a breaking change by specifying the major and minor version numbers are as expected.  Note that this requires a release of natlinkcore if the minor version of natlink changes.  At minimum this will require an update to pyproject.toml and a release to pypi, even if no python code has changed. 



This is how the version specifier should look for natlink (subsituting the version numbers appropriate).  In this case, we are saying that any natlink 5.5 is required, and that 
we require greater than 5.5.7 as well because we are relying on a non-breaking change introduced in 5.5.7.
`    "natlink ~= 5.5, >= 5.5.7"
`
Often, the natlink dependancy should just specify the major and minor version:
`
    "natlink ~= 5.5"
`

You could have a case where natlinkcore works with natlink 5.5 and 5.6, you could express this in pyproject.toml as
    "natlink ~= 5.5, ~= 5.6".  


## Debugging Instructions

Read the detailed developer instructions for setting up the debugger.  You can look in this projects tree until 
documentation/developers.rst.

