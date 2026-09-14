#pylint:disable= C0114, C0116, W0401, W0614, W0621, W0108, W0212, C3001,C0413, W0107, R0915


from pathlib import Path
from distutils.dir_util import copy_tree
from distutils.file_util import copy_file
# import sys
import os
import copy
from pprint import pprint
# import sysconfig
import pytest
from natlinkcore import config

from natlinkcore.configure import natlinkconfig_cli
from natlinkcore.configure import natlinkconfigfunctions

thisDir = Path(__file__).parent
configDir = os.path.normpath(thisDir/'../src/natlinkcore/configure')
# sys.path.insert(0, configDir)
# print(f'sys.path: {sys.path}')

# import natlinkconfig_cli
# import natlinkconfigfunctions

def return_true(*args):
    return True

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

def test_config_check_config_file(vocola_config_setup):
    """test the basics of the config file natlink.ini
    
    remove non existing directories,
    
    remove or correct obsolete or changed options (unimacro, vocola)
    
    """
    natlink_config_dir, _vocola_userdir = vocola_config_setup
    copy_file(str(thisDir/"samples"/"sample_old_natlink.ini"), str(natlink_config_dir/'natlink.ini'))
    config = natlinkconfigfunctions.NatlinkConfig()
    result = config.status.getVocolaTakesUniactions()
    assert result is False

    config.check_config()
    # internal functions gives string, not bool:
    result = config.config_get('vocola', 'vocolatakesuniactions')
    assert result.lower() == 'true'
    ## note this is handled in the loader.py via a smarter config_get function!!!
    ## so the preferred call is:::
    result = config.status.getVocolaTakesUniactions()
    assert result is True
    
def test_check_elevated_mode_tt(cli, monkeypatch):
    """try the variants of am_elevated and want_elevated
    result True
    """
    def return_true():
        return True
    # def return_false():
    #     return False
    monkeypatch.setattr(cli, 'am_elevated', return_true)
    monkeypatch.setattr(cli, 'want_elevated', return_true)
    result = cli.check_elevated_mode()
    assert result is True
    
def test_check_elevated_mode_ff(cli, monkeypatch):
    """try the variants of am_elevated and want_elevated
    result True
    """
    # def return_true():
    #     return True
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
    

def test_prefix_home_appdata(cli):
    """check the existence of environment variables for shortening the path of a directory
    
    No "~" any more, use "localappdata". Most used for natlink config files!!!
    Also check "appdata", which expands to the roaming appdata directory (Handle with care!!!)
    
    Check this with values on your computer, monkeypatching does not seem to worth the trouble...
    """
    # to_prefix = config.expand_path('%localappdata%\\Microsoft')
    ### this happens when testing all the functions. When doing only
    ### this test function, all is OK.
    # assert to_prefix != ''
    # prefixed  = cli.Config.prefix_home_appdata(to_prefix)
    # assert prefixed == '%localappdata%\\Microsoft'
    # 
    # # the isdir check skipped, as %localappdata% can be changed because of
    # # test purposes...
    # expanded = config.expand_path(prefixed)
    # assert expanded == to_prefix
    
    # check %appdata% (roaming)
    to_prefix = config.expand_path('%appdata%\\Microsoft')
    prefixed  = cli.Config.prefix_home_appdata(to_prefix)
    assert prefixed == '%appdata%\\Microsoft'

    expanded = config.expand_path(prefixed)
    assert os.path.isdir(expanded)
    
    # check %personalhome% (~)
    to_prefix = config.expand_path('%personalhome%\\Documents')
    prefixed  = cli.Config.prefix_home_appdata(to_prefix)
    assert prefixed == '%personalhome%\\Documents'

    expanded = config.expand_path(prefixed)
    assert os.path.isdir(expanded)
    assert to_prefix == expanded
    
    # expand the previous "~":
    prefixed = "~\\Documents"
    expanded = config.expand_path(prefixed)
    assert os.path.isdir(expanded)
    prefixed_new  = cli.Config.prefix_home_appdata(expanded)
    assert prefixed_new == '%personalhome%\\Documents'
    
    
def test_enable_disable_vocola(vocola_config_setup, cli, monkeypatch):
    """enable and disable vocola.
    
    (ALSO: trying the test procedure from conftest.py)
    (Only one language, enx, side effect: change 'Unimacro(' to 'Usc('
    Enable with Uniactions OFF, later 
    ASSUME: vocola is already a valid module!!! in this test pipping the package vocola2
            is skipped...
    """
    monkeypatch.setattr(cli.Config, "pip_package", return_true)
    natlink_config_dir, vocola_userdir = vocola_config_setup
    
    print(f'natlink_config_dir: {natlink_config_dir}')
    print(f'vocola_userdir: {vocola_userdir}')
    assert os.path.isdir(natlink_config_dir)
    assert os.path.isdir(vocola_userdir)
    assert os.path.isfile(natlink_config_dir/'natlink.ini')

    #copy a simple sample, only enx files
    copy_tree(str(thisDir/"samples"/"vocola_userdir_1"),str(vocola_userdir))
    
    folder_dict = get_folder_dict(vocola_userdir)
    # should be equal to above directory vocola_userdir_2
    exp_dict = {'_vocola.vcl': ['# global vocola command file for language: enx',
                 'Paste Test = HeardWord("Paste", "Box");',
                 'unimacro test = Usc(T;W);'],
 'empty.vcl': [],
 'firefox.vcl': ['# vocola file for language: enx',
                 '# Voice commands for firefox',
                 'go to search = {ctrl+t}{ctrl+k};',
                 'view source = {ctrl+u};']}
    
    cli.do_v(vocola_userdir)
    assert cli.Config.status.vocolaIsEnabled()
    assert cli.Config.status.getVocolaTakesUniactions() is False

   # check new state:
    folder_dict = get_folder_dict(vocola_userdir)

    if exp_dict != folder_dict:
        print('\n=================================\n')
        print('AFTER enable_vocola (do_v):')
        print('If this is the correct content of vocola_userdir now')
        print('please change your test file above accordingly\n')

        pprint(folder_dict)
        assert False

 

    # basic test with 
    cli.do_V(None)
    result = cli.Config.status.vocolaIsEnabled()
    assert not result
    
    folder_dict = get_folder_dict(vocola_userdir)

    if exp_dict != folder_dict:
        print('\n=================================\n')
        print('AFTER disable_vocola (do_V):')
        print('If this is the correct content of vocola_userdir now')
        print('please change your test file above accordingly\n')

        pprint(folder_dict)
        assert False
    
    
    cli.do_v(vocola_userdir)
    assert cli.Config.status.vocolaIsEnabled()
    
    assert cli.Config.status.getVocolaTakesUniactions() is False

    folder_dict = get_folder_dict(vocola_userdir)

    if exp_dict != folder_dict:
        print('\n=================================\n')
        print('AFTER second enable_vocola (do_v):')
        print('If this is the correct content of vocola_userdir now')
        print('please change your test file above accordingly\n')

        pprint(folder_dict)
        assert False


    
    ## try to activate this option
    cli.do_a(vocola_userdir)
    
    assert cli.Config.status.getVocolaTakesUniactions() is True

    folder_dict = get_folder_dict(vocola_userdir)

    exp_dict_uniactions = {'Uniactions.vch': '> 20 lines',
 '_vocola.vcl': ['include Uniactions.vch;',
                 '# global vocola command file for language: enx',
                 'Paste Test = HeardWord("Paste", "Box");',
                 'unimacro test = Usc(T;W);'],
 'empty.vcl': ['include Uniactions.vch;'],
 'firefox.vcl': ['include Uniactions.vch;',
                 '# vocola file for language: enx',
                 '# Voice commands for firefox',
                 'go to search = {ctrl+t}{ctrl+k};',
                 'view source = {ctrl+u};']}

    if exp_dict_uniactions!= folder_dict:
        print('\n=================================\n')
        print('AFTER enable VocolaTakesUniactions (do_a):')
        print('If this is the correct content of vocola_userdir now')
        print('please change your test file above accordingly\n')

        pprint(folder_dict)
        assert False



    ## try to deactivate this option
    # NOTE: this option also removes Uniactions.vch
    cli.do_A(vocola_userdir)
    assert cli.Config.status.getVocolaTakesUniactions() is False

    folder_dict = get_folder_dict(vocola_userdir)

    exp_dict = {'_vocola.vcl': ['# global vocola command file for language: enx',
                 'Paste Test = HeardWord("Paste", "Box");',
                 '#Usc#unimacro test = Usc(T;W);'],
 'empty.vcl': [],
 'firefox.vcl': ['# vocola file for language: enx',
                 '# Voice commands for firefox',
                 'go to search = {ctrl+t}{ctrl+k};',
                 'view source = {ctrl+u};']}


    if exp_dict != folder_dict:
        print('\n=================================\n')
        print('AFTER disable VocolaTakesUniactions (do_A):')
        print('If this is the correct content of vocola_userdir now')
        print('please change your test file above accordingly\n')

        pprint(folder_dict)
        assert False
    
    
    folder_dict = get_folder_dict(vocola_userdir)
    assert exp_dict == folder_dict

    cli.do_V(None)
    assert cli.Config.status.vocolaIsEnabled() is False
    assert not result   

    folder_dict = get_folder_dict(vocola_userdir)
    assert exp_dict == folder_dict


    ## try to activate this option when vocola is disabled:
    ## option passes, only config file is checked.
    cli.do_a(vocola_userdir)
    result = cli.Config.status.getVocolaTakesUniactions()
    assert not result

    ## try to deactivate this option when vocola is disabled:
    cli.do_A(vocola_userdir)
    assert cli.Config.status.getVocolaTakesUniactions() is False
    
def test_vocola_include_lines_valid_path(vocola_config_setup, cli, monkeypatch):
    """check if the include lines are inserted/deleted with the option v (enable vocola)

    With new vocola config (enx not a sub directory any more, always taking vocola multiple languages),
    the include paths of include files can present problems. They are tackled with
    checkVocolaIncludeLinesValidPath, and tested here, together with other testing...
    
    This is NOT for Uniactions.vch include lines, assume VocolaTakesUniactions is False
    
    ASSUME: vocola is already a valid module!!! in this test pipping the package vocola2
            is skipped...
    """
    monkeypatch.setattr(cli.Config, "pip_package", return_true)
    natlink_config_dir, vocola_userdir = vocola_config_setup
    print(f'natlink_config_dir: {natlink_config_dir}')
    print(f'vocola_userdir: {vocola_userdir}')
    assert os.path.isdir(natlink_config_dir)
    assert os.path.isdir(vocola_userdir)
    assert os.path.isfile(natlink_config_dir/'natlink.ini')

    #copy a sample enx and nld, which should end up in empty files or files
    #only containting the wanted include line...
    copy_tree(str(thisDir/"samples"/"vocola_userdir_include"),str(vocola_userdir))
    cli.Config.config_set('vocola', 'vocolatakesuniactions', False)

    folder_dict = get_folder_dict(vocola_userdir)
    start_dict = {'generalincl.vch': ['#include file general refer to specialinclude.vch:',
                     'include specialinclude.vch;'],
 'grammar.vcl': ['include Uniactions.vch;',
                 '# should be changed to nld\\ and reactivated:',
                 'include ..\\nld\\specialinclude_nld.vch;',
                 'include ..\\nld\\nonexist.vch;',
                 'include command = include_command;'],
 'nld---generalincl_nld.vch': ['# include_nld',
                               'include ..\\specialinclude.vch;'],
 'nld---grammar_nld.vcl': ['include ..\\Uniactions.vch;',
                           'include Uniactions.vch;',
                           'include "generalincl_nld.vch";',
                           'include nonexist.vch;',
                           '# should be changed to ..\\:',
                           'include ..\\enx\\generalincl.vch;',
                           'include command = include_command;'],
 'nld---specialinclude_nld.vch': ['# include_nld',
                                  'include ..\\specialinclude.vch;'],
 'specialinclude.vch': ['# include file special with Uniactions lines',
                        '#function definition:',
                        'login(n,p) := "blah_blah" LW();']}

    # print('folder_dict, actual folder dict at start:')
    # pprint(folder_dict)
    assert start_dict == folder_dict
    
    cli.do_v(vocola_userdir)
    assert cli.Config.status.vocolaIsEnabled()
    result = cli.Config.status.getVocolaTakesUniactions() 
    assert not result

    exp_dict = {'generalincl.vch': ['#include file general refer to specialinclude.vch:',
                     'include specialinclude.vch;'],
 'grammar.vcl': ['# should be changed to nld\\ and reactivated:',
                 'include nld\\specialinclude_nld.vch;',
                 '#invalidfile#include ..\\nld\\nonexist.vch;',
                 'include command = include_command;'],
 'nld---generalincl_nld.vch': ['# include_nld',
                               'include ..\\specialinclude.vch;'],
 'nld---grammar_nld.vcl': ['include generalincl_nld.vch;',
                           '#invalidfile#include nonexist.vch;',
                           '# should be changed to ..\\:',
                           'include ..\\generalincl.vch;',
                           'include command = include_command;'],
 'nld---specialinclude_nld.vch': ['# include_nld',
                                  'include ..\\specialinclude.vch;'],
 'specialinclude.vch': ['# include file special with Uniactions lines',
                        '#function definition:',
                        'login(n,p) := "blah_blah" LW();']}
   
   
    folder_dict = get_folder_dict(vocola_userdir)

 
    if exp_dict != folder_dict:
        print('\n=================================\n')
        print('AFTER testing check vocola valid include lines:')
        print('If this is the correct content of vocola_userdir now')
        print('please change your test file above accordingly\n')

        pprint(folder_dict)
        assert False
    
   ### now switch on Uniactions:
        
    cli.do_a(True)         
    exp_dict = {'Uniactions.vch': '> 20 lines',
 'generalincl.vch': ['#include file general refer to specialinclude.vch:',
                     'include specialinclude.vch;'],
 'grammar.vcl': ['include Uniactions.vch;',
                 '# should be changed to nld\\ and reactivated:',
                 'include nld\\specialinclude_nld.vch;',
                 '#invalidfile#include ..\\nld\\nonexist.vch;',
                 'include command = include_command;'],
 'nld---generalincl_nld.vch': ['# include_nld',
                               'include ..\\specialinclude.vch;'],
 'nld---grammar_nld.vcl': ['include ..\\Uniactions.vch;',
                           'include generalincl_nld.vch;',
                           '#invalidfile#include nonexist.vch;',
                           '# should be changed to ..\\:',
                           'include ..\\generalincl.vch;',
                           'include command = include_command;'],
 'nld---specialinclude_nld.vch': ['# include_nld',
                                  'include ..\\specialinclude.vch;'],
 'specialinclude.vch': ['# include file special with Uniactions lines',
                        '#function definition:',
                        'login(n,p) := "blah_blah" LW();']}
   
    folder_dict = get_folder_dict(vocola_userdir)

 
    if exp_dict != folder_dict:
        print('\n=================================\n')
        print('AFTER testing check vocola valid include lines, with Uniactions switched ON:')
        print('If this is the correct content of vocola_userdir now')
        print('please change your test file above accordingly\n')

        pprint(folder_dict)
        assert False


        

def test_vocola_include_lines_take_uniactions_off(vocola_config_setup, cli, monkeypatch):
    """check if the include lines are correctly deleted when option vocolatakesuniactions is initially OFF

    it is about the functions: includeUniactionsVchLineInVocolaFiles and removeUniactionsVchLineInVocolaFiles
    in natlinkconfigfunctions.py.

    ASSUME: vocola is already a valid module!!! in this test pipping the package vocola2
            is skipped...
    """
    monkeypatch.setattr(cli.Config, "pip_package", return_true)
    natlink_config_dir, vocola_userdir = vocola_config_setup
    
    print(f'natlink_config_dir: {natlink_config_dir}')
    print(f'vocola_userdir: {vocola_userdir}')
    assert os.path.isdir(natlink_config_dir)
    assert os.path.isdir(vocola_userdir)
    assert os.path.isfile(natlink_config_dir/'natlink.ini')


    copy_tree(str(thisDir/"samples"/"vocola_userdir_2"),str(vocola_userdir))
    # There we go:
    # cli.do_A(True)
    cli.do_v(vocola_userdir)
    assert cli.Config.status.vocolaIsEnabled()
    assert not cli.Config.status.getVocolaTakesUniactions()
    # includeFile should have been copied, irrespective of the VocolaTakesUniactions
    
    folder_dict = get_folder_dict(vocola_userdir)
    
    exp_dict = {'empty.vcl': [],
 'nld---empty_nld.vcl': [],
 'nld---oldlines_nld.vcl': [],
 'oldlines.vcl': []}
    
    if exp_dict != folder_dict:
        print('\n=================================\n')
        print('AFTER enable vocola with option vocolatakesuniactions OFF:')
        print('If this is the correct content of vocola_userdir now')
        print('please change your test file above accordingly\n')

        pprint(folder_dict)
        assert False
        
    # this should not change anything: (disabling vocolatakesuniactions (again))        
    cli.do_A(None)
    folder_dict = get_folder_dict(vocola_userdir)
    
    exp_dict = {'empty.vcl': [],
 'nld---empty_nld.vcl': [],
 'nld---oldlines_nld.vcl': [],
 'oldlines.vcl': []}
    
    if exp_dict != folder_dict:
        print('\n=================================\n')
        print('AFTER enable vocola with option vocolatakesuniactions OFF:')
        print('If this is the correct content of vocola_userdir now')
        print('please change your test file above accordingly\n')

        pprint(folder_dict)
        assert False
    
    # now enable vocolatakesuniactions:
    cli.do_a(None)
    folder_dict = get_folder_dict(vocola_userdir)
    
    exp_dict = {'Uniactions.vch': '> 20 lines',
 'empty.vcl': ['include Uniactions.vch;'],
 'nld---empty_nld.vcl': ['include ..\\Uniactions.vch;'],
 'nld---oldlines_nld.vcl': ['include ..\\Uniactions.vch;'],
 'oldlines.vcl': ['include Uniactions.vch;']}
    
    if exp_dict != folder_dict:
        print('\n=================================\n')
        print('AFTER setting option vocolatakesuniactions to ON:')
        print('If this is the correct content of vocola_userdir now')
        print('please change your test file above accordingly\n')

        pprint(folder_dict)
        assert False

    
def test_vocola_correctLineUsc():
    """testing commenting out or uncommenting Uniaction lines, in use by Vocola configuration
    
    Take multiline commands into consideration!!!
    The main issue is with UscIsOff (deciding which lines to comment), which as a side
    effect also changes "Unimacro(" into "Usc("!!
    for function: correctLineUsc
    
    """
    nc = natlinkconfigfunctions.NatlinkConfig()
    UscIsOn, UscIsOff = True, False

    lines = ['highlight <_anything> = Unimacro(<<startsearch>>) $1', 'Unimacro(<<searchgo>>);']
    line2 = nc.CorrectLineUsc(lines, UscIsOff)
    exp_list = ['#Usc#highlight <_anything> = Usc(<<startsearch>>) $1', '#Usc#Usc(<<searchgo>>);']
    assert exp_list == line2.split('\n')
    
    line = nc.CorrectLineUsc(exp_list[0], UscIsOn)
    assert line == 'highlight <_anything> = Usc(<<startsearch>>) $1'
    
    lines = ['highlight <_anything> =', '#comment line with Unimacro(longago)', 'Unimacro(<<startsearch>>) $1']
    line2 = nc.CorrectLineUsc(lines, UscIsOff)
    exp = '#Usc#highlight <_anything> =\n#Usc##comment line with Usc(longago)\n#Usc#Usc(<<startsearch>>) $1'
    assert exp == line2

    single_line_Date =  'Date = DATE1(%m/%d/%Y) ;'
    result = nc.CorrectLineUsc(single_line_Date, UscIsOff)
    exp = '#Usc#' + single_line_Date
    assert exp == result
    
    # no Usc commands:

    lines_no_usc = ['multiple = ', 'Hello_world;']
    result = nc.CorrectLineUsc(lines_no_usc, UscIsOff)
    assert result == '\n'.join(lines_no_usc)

    lines_no_usc = ['multiple comment = ','#comment one', '#comment two', 'Hello_world;']
    result = nc.CorrectLineUsc(lines_no_usc, UscIsOff)
    assert result == '\n'.join(lines_no_usc) 


    # these only with UscIsOff:

    lines_with_usc = ['multiple with Usc = ', 'Hello_world', 'S(abc);']
    result = nc.CorrectLineUsc(lines_with_usc, UscIsOff)
    expected =  '\n'.join(['#Usc#multiple with Usc = ', '#Usc#Hello_world', '#Usc#S(abc);'])
    assert result == expected
    
    lines_no_usc = ['Quasi Usc in command WINKEY = ', 'Hello_world', 'NO real Usc;']
    result = nc.CorrectLineUsc(lines_no_usc, UscIsOff)
    assert result == '\n'.join(lines_no_usc)

    lines_no_usc = ['Quasi Usc in command WINKEY = ', 'Hello_world', 'NO real Usc;']
    result = nc.CorrectLineUsc(lines_no_usc, False)
    assert result == '\n'.join(lines_no_usc)

    lines_with_usc = ['multiple with Usc = ', 'Hello_world', 'S(abc);']
    result = nc.CorrectLineUsc(lines_with_usc, False)
    expected =  '\n'.join(['#Usc#multiple with Usc = ', '#Usc#Hello_world', '#Usc#S(abc);'])
    assert result == expected

    line_with_unimacro = ['single obsolete line = Unimacro("hello");']
    result = nc.CorrectLineUsc(line_with_unimacro, False)
    expected =  '#Usc#single obsolete line = Usc("hello");'
    assert result == expected
    
    
    
    
def get_folder_dict(folderpath):
    """return the contenst in a dict, assume all text files
    
    rstrip all lines
    """
    join = os.path.join
    D = {}
    folderdir = str(folderpath)
    len_prefix = len(folderdir)
    
    for dirpath, _dirnames, files in os.walk(folderdir):
        # print(f'Found directory: {dirpath}')
        subdir = dirpath[len_prefix+1:]
        key_prefix = f'{subdir}---' if subdir else ''
        for fi in files:
            with open(join(dirpath, fi), 'r', encoding='utf-8') as f:
                lines = [line.rstrip(' \n') for line in f if line.strip()]
            D[key_prefix + fi] = lines if len(lines) <= 20 else '> 20 lines'
            
    return D
    
def _main():
    """run pytest for this module
    """
    pytest.main(['-s', 'test_natlinkconfig.py'])
    # pytest.main(['-s', '-vv','test_natlinkconfig.py::test_vocola_include_lines_valid_path'])

 
if __name__ == "__main__":
    _main() 

