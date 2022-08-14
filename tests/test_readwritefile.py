
#pylint:disable= C0114, C0116, R1732
import os
import configparser
from typing import List
import pytest
from natlinkcore.readwritefile import ReadWriteFile

thisFile = __file__
thisDir, Filename = os.path.split(thisFile)
testDir = os.path.join(thisDir, 'mock_readwritefile')
outputDir = os.path.join(thisDir, 'scratch_readwritefile')


def setup_module(module):
    if not os.path.isdir(outputDir):
        os.mkdir(outputDir)

def teardown_module(module):
    for F in os.listdir(outputDir):
        F_path = os.path.join(outputDir, F)
        os.remove(F_path)

def sample_rwfile(sample_name: str) -> List:
    """
    give the full path of a test sample file and the corresponding outputfile
    """
    inp_path = os.path.join(testDir, sample_name)
    out_path = os.path.join(outputDir, sample_name)
    return [inp_path, out_path]

#easier than using the decorator syntax
def make_sample_paths(sample_filename):
    return pytest.fixture(lambda : sample_rwfile(sample_filename))

ini_path = make_sample_paths('natlinkinisample.ini')

def test_only_write_file():
    join, isfile = os.path.join, os.path.isfile
    newFile = join(outputDir, 'output-newfile.txt')
    if isfile(newFile):
        os.unlink(newFile)
    rwfile = ReadWriteFile()
    text = ''
    rwfile.writeAnything(newFile, text)
    assert open(newFile, 'rb').read() == b''
 
    # read back empty file:
    rwfile = ReadWriteFile()
    text = rwfile.readAnything(newFile)
    assert rwfile.encoding == 'ascii'
    assert rwfile.bom == ''
    assert text == ''
    
# def test_accented_characters_write_file():
#     join, isfile = os.path.join, os.path.isfile
#     newFile = join(testDir, 'output-accented.txt')
#     if isfile(newFile):
#         os.unlink(newFile)
#     text = 'caf\xe9'
#     rwfile = ReadWriteFile(encodings=['ascii'])  # optional encoding
#     # this is with default errors='xmlcharrefreplace':
#     rwfile.writeAnything(newFile, text)
#     testTextBinary = open(newFile, 'rb').read()
#     wanted = b'caf&#233;'
#     assert testTextBinary == wanted
#     # same, default is 'xmlcharrefreplace':
#     rwfile.writeAnything(newFile, text, errors='xmlcharrefreplace')
#     testTextBinary = open(newFile, 'rb').read()
#     assert testTextBinary == b'caf&#233;'
#     assert len(testTextBinary) == 9
# 
#     text_back = rwfile.readAnything(newFile)
#     assert text_back == 'caf&#233;'
#     
#     rwfile.writeAnything(newFile, text, errors='replace')
#     testTextBinary = open(newFile, 'rb').read()
#     assert testTextBinary == b'caf?'
#     assert len(testTextBinary) == 4
#     rwfile.writeAnything(newFile, text, errors='ignore')
#     testTextBinary = open(newFile, 'rb').read()
#     assert testTextBinary == b'caf'
#     assert len(testTextBinary) == 3
#     
#     rwfile_utf = ReadWriteFile(encodings=['utf-8'])
#     text = 'Caf\xe9'
#     rwfile_utf.writeAnything(newFile, text)
#     text_back = rwfile_utf.readAnything(newFile)
#     assert text == text_back
# 
# def test_other_encodings_write_file():
#     join = os.path.join
#     oldFile = join(testDir, 'latin1 accented.txt')
#     rwfile = ReadWriteFile(encodings=['latin1'])  # optional encoding
#     text = rwfile.readAnything(oldFile)
#     assert text == 'latin1 café'
#     
#     
#     
# 
# 
# def test_latin1_cp1252_write_file():
#     join = os.path.join
#     _newFile = join(testDir, 'latin1.txt')
#     _newFile = join(testDir, 'cp1252.txt')
#     # TODO (QH) to be done, these encodings do not take all characters,
#     # and need special attention.
#     # (as long as the "fallback" is utf-8, all write files should go well!)

def test_read_config_file(ini_path):
    # 
    # listdir, join, splitext = os.listdir, os.path.join, os.path.splitext
    # for F in listdir(testDir):
    #     if F.endswith('.ini'):
    #         if F == 'acoustics.ini':
    #             F_path = join(testDir, F)
    #             rwfile = ReadWriteFile()
    #             config_text = rwfile.readAnything(F_path)
    #             Config = configparser.ConfigParser()
    #             Config.read_string(config_text)
    #             assert Config.get('Acoustics', '2 2') == '2_2' 
    #             continue
    in_path, out_path = ini_path
    rwfile = ReadWriteFile()
    config_text = rwfile.readAnything(in_path)
    Config = configparser.ConfigParser()
    Config.read_string(config_text)
    assert Config.get('settings', 'log_level') == 'DEBUG'
    Config.set('settings', 'log_level', 'INFO')
    assert Config.get('settings', 'log_level') == 'INFO'
    
    Config.write(open(out_path, 'w', encoding=rwfile.encoding))

if __name__ == "__main__":
    pytest.main(['test_readwritefile.py'])
    