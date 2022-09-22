#powershell to run the tests, then build the python package.
$ErrorActionPreference = "Stop"
py -m pytest 
py -m flit publish 