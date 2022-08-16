import pytest
import natlink as n
import pathlib as p
import sys
import sysconfig
import os
#mock_userdir copied from test_config.py


#workaround for monkeypatching at module scope
#see https://stackoverflow.com/questions/53963822/python-monkeypatch-setattr-with-pytest-fixture-at-module-scope

@pytest.fixture(scope='module')
def monkeymodule():
    from _pytest.monkeypatch import MonkeyPatch
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="module")
def natlink_connection(monkeymodule):
    mock_folder=p.WindowsPath(os.path.dirname(__file__)) / "mock_userdir"
    monkeymodule.setenv("natlink_userdir",str(mock_folder))

    print("\nConnecting natlink")
    yield n.natConnect()  #will be none
    print("\nDisconnecting natlink")
    n.natDisconnect()

@pytest.fixture(scope="module")
def mock_userdir(monkeypatch):
    mock_folder=p.WindowsPath(os.path.dirname(__file__)) / "mock_userdir"
    print(f"Mock Userdir Folder {mock_folder}")
    monkeypatch.setenv("natlink_userdir",str(mock_folder))


test0="brachialis"   #a word
test1="american ansi english phrase"  #
test2="naïve"                         # ï diareses
test3="Québec-City"                   # é accent
test4 = f"{test2} in {test3} phrase"     #phrase       


phrases = [test0,test1,test2,test3,test4]
strings_to_play=zip(phrases,phrases)

@pytest.mark.parametrize('string_to_play',phrases)
def test_playstring(string_to_play,natlink_connection):
    #leave lots of print statements in as the test might hang.
    print("\nWarning, if this test seems to hang, kill any shells where you have run this test through pytest.  \n"
            "This test is fragile and can hang your shell if something goes wrong") 
    s=string_to_play
    print(f"\nplaying {s}")
    n.playString(s+"\n")
    i=input(f"\nattemtping to read {s}\n")
    print(f"\nread {i}")
    assert s == i

    

 

