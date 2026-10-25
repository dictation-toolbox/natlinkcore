# this is a special file of pytest, the name is confusing since we have our own test_config.py
# it has  a  purpose you can read about in the pytest documentation.
#only needs to be called once
#pylint:disable = C0411, W4901
# from string import Template
from pathlib import Path
import pytest
import natlink
from functools import cache
import importlib
from shutil import copy as file_copy
# from shutil import copytree
thisDir = Path(__file__).parent


@cache          
def vocola_source_dir() ->Path:
    return Path(importlib.util.find_spec("vocola2").submodule_search_locations[0])



@pytest.fixture()
def vocola_config_setup(tmpdir):
  
    tmp_test_root = tmpdir
    # tmp_test_root functions as localappdata!
    natlink_config_dir=tmp_test_root.mkdir('Natlink')
    natlink_config_file=natlink_config_dir/"natlink.ini"
    vocola_userdir=tmp_test_root.mkdir("vocola_user_directory")
    natlink_usergrammars_dir=tmp_test_root.mkdir("natlink_user_grammars")
    sub={
        'vocolatestuserdirectory':vocola_userdir,
        'natlinktestuserdirectory':natlink_usergrammars_dir
    }  
    # natlinkini_source_folder = Path(__file__).parent / "vocola_test_natlink_config.natlink"
    # natlinkini_source_config = natlinkini_source_folder/"_natlink.ini"
    # with open(natlinkini_source_config, encoding='utf-8') as f:
    #     src=Template(f.read())
    #     config_file_text=src.substitute(sub)
    # 
    # print(f"natlink_config_dir: {natlink_config_dir}")
    # with open(natlink_config_file,'w', encoding='utf-8') as fw:
    #     fw.write(config_file_text)
    # 
    # #copy the unimacro user directory to the unimacro_user_directory
    # copy_tree(str(thisDir/"test_sample_vocola_userdir"),str(vocola_userdir))

    pytest.MonkeyPatch().setenv("NATLINK_SETTINGSDIR",str(natlink_config_dir))
    pytest.MonkeyPatch().setenv("localappdata",str(tmp_test_root))
    yield [natlink_config_dir,vocola_userdir]

@pytest.fixture()
def vocola_setup(vocola_config_setup):
    """used for testing vocola with dragon running
    """
    oo=natlink.natConnect()
    L = vocola_config_setup
    L.append(oo)
    yield L
    natlink.natDisconnect()
    
