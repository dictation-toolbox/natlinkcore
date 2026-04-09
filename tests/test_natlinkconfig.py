#pylint:disable= C0114, C0116, W0401, W0614, W0621, W0108, W0212, C3001,C0413

from pathlib import Path
import sys
import os
import sysconfig
import pytest

thisDir = Path(__file__).parent
configDir = os.path.normpath(thisDir/'../src/natlinkcore/configure')
sys.path.append(configDir)
print(f'sys.path: {sys.path}')

import natlinkconfig_cli
import natlinkconfigfunctions

@pytest.fixture
def cli():
    """return the (non interactive) cli
    """
    _cli = natlinkconfig_cli._main()
    return _cli


def test_run_natlinkconfig_cli():
    _nc = natlinkconfigfunctions.NatlinkConfig()
    _config = _nc.Config
    _doc_path = _nc.documents_path
    _home_path = _nc.home_path
    _natlinkconfig_path = _nc.natlinkconfig_path
    print(f'natlinkconfig_path: {_natlinkconfig_path}')
    _cli = natlinkconfig_cli._main()
    print(f'natlinkconfig_cli: {_cli}')
    
    pass

def test_config_cli(cli, capsys):
    """test the basics of the natlinkconfig_cli program
    """
    cli.do_i('dummy')
    output = capsys.readouterr().out.rstrip()
    
    assert output.find('NatlinkDirectory') > 0
    
def test_check_elevated_mode_tt(cli, monkeypatch):
    """try the variants of am_elevated and want_elevated
    result True
    """
    def return_true():
        return True
    def return_false():
        return False
    monkeypatch.setattr(cli, 'am_elevated', return_true)
    monkeypatch.setattr(cli, 'want_elevated', return_true)
    result = cli.check_elevated_mode()
    assert result is True
    
def test_check_elevated_mode_ff(cli, monkeypatch):
    """try the variants of am_elevated and want_elevated
    result True
    """
    def return_true():
        return True
    def return_false():
        return False
    monkeypatch.setattr(cli, 'am_elevated', return_false)
    monkeypatch.setattr(cli, 'want_elevated', return_false)
    result = cli.check_elevated_mode()
    assert result is True
    
def test_check_elevated_mode_tf(cli, monkeypatch):
    """try the variants of am_elevated and want_elevated
    result False
    """
    def return_true():
        return True
    def return_false():
        return False
    monkeypatch.setattr(cli, 'am_elevated', return_true)
    monkeypatch.setattr(cli, 'want_elevated', return_false)
    result = cli.check_elevated_mode()
    assert result is False
    
def test_check_elevated_mode_ft(cli, monkeypatch):
    """try the variants of am_elevated and want_elevated
    result False
    """
    def return_true():
        return True
    def return_false():
        return False
    monkeypatch.setattr(cli, 'am_elevated', return_false)
    monkeypatch.setattr(cli, 'want_elevated', return_true)
    result = cli.check_elevated_mode()
    assert result is False

def test_check_elevated_mode_with_do_F(cli, monkeypatch):
    """try the variants of am_elevated overridden by do_F
    result is then True (after first a False)
    """
    def return_true():
        return True
    def return_false():
        return False
    monkeypatch.setattr(cli, 'am_elevated', return_false)
    monkeypatch.setattr(cli, 'want_elevated', return_true)
    result = cli.check_elevated_mode()
    assert result is False
    # now force accepting am_elevated:
    cli.do_F('dummy')
    monkeypatch.setattr(cli, 'am_elevated', return_true)
    result = cli.check_elevated_mode()
    assert result is True
    
def test_check_elevated_mode_with_do_f(cli, monkeypatch):
    """try the variants of am_elevated overridden by do_F
    result is then True (after first a False)
    """
    def return_true():
        return True
    def return_false():
        return False
    monkeypatch.setattr(cli, 'am_elevated', return_true)
    monkeypatch.setattr(cli, 'want_elevated', return_false)
    result = cli.check_elevated_mode()
    assert result is False
    # now force accepting am_elevated to false, non elevated
    cli.do_f('dummy')
    monkeypatch.setattr(cli, 'am_elevated', return_false)
    result = cli.check_elevated_mode()
    assert result is True
    
    

def _main():
    """run pytest for this module
    """
    pytest.main(['test_natlinkconfig.py'])


if __name__ == "__main__":
    _main()

