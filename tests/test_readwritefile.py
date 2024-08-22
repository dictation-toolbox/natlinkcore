
#pylint:disable= C0114, C0116, R1732
import os
import configparser
import pytest
import filecmp
from natlinkcore.readwritefile import ReadWriteFile
from pathlib import Path

thisFile = __file__
thisDir, Filename = os.path.split(thisFile)
testDir = os.path.join(thisDir, 'readwritefiletest')
testFolderName="readwritefiletest"

mock_readwritefiledir=Path(thisDir)/"mock_readwritefile"

def setup_module(module):
    pass

def teardown_module(module):
    for F in os.listdir(testDir):
        if F.startswith('output-'):
            F_path = os.path.join(testDir, F)
            os.remove(F_path)

def test_only_write_file(tmp_path):
    print(f"Temp path: {tmp_path}")
    testDir = tmp_path / testFolderName
    testDir.mkdir()

 #   join, isfile = os.path.join, os.path.isfile
 #   newFile = join(testDir, 'output-newfile.txt')
 #   if isfile(newFile):
 #       os.unlink(newFile)
    newFile= testDir/'output-newfile.txt'
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
    
def test_accented_characters_write_file(tmp_path):
#    join, isfile = os.path.join, os.path.isfile
#    testDir = tmp_path / testFolderName
#    testDir.mkdir()
 #   newFile = join(testDir, 'output-accented.txt')
    testDir = tmp_path / testFolderName
    testDir.mkdir()
    newFile = testDir/"output-accented.txt"
    text = 'caf\xe9'
    rwfile = ReadWriteFile(encodings=['ascii'])  # optional encoding
    # this is with default errors='xmlcharrefreplace':
    rwfile.writeAnything(newFile, text)
    testTextBinary = open(newFile, 'rb').read()
    wanted = b'caf&#233;'
    assert testTextBinary == wanted
    # same, default is 'xmlcharrefreplace':
    rwfile.writeAnything(newFile, text, errors='xmlcharrefreplace')
    testTextBinary = open(newFile, 'rb').read()
    assert testTextBinary == b'caf&#233;'
    assert len(testTextBinary) == 9

    text_back = rwfile.readAnything(newFile)
    assert text_back == 'caf&#233;'
    
    rwfile.writeAnything(newFile, text, errors='replace')
    testTextBinary = open(newFile, 'rb').read()
    assert testTextBinary == b'caf?'
    assert len(testTextBinary) == 4
    rwfile.writeAnything(newFile, text, errors='ignore')
    testTextBinary = open(newFile, 'rb').read()
    assert testTextBinary == b'caf'
    assert len(testTextBinary) == 3
    
    rwfile_utf = ReadWriteFile(encodings=['utf-8'])
    text = 'Caf\xe9'
    rwfile_utf.writeAnything(newFile, text)
    text_back = rwfile_utf.readAnything(newFile)
    assert text == text_back

def test_other_encodings_write_file(tmp_path):
     
    testDir = tmp_path / testFolderName
    testDir.mkdir()

    oldFile = mock_readwritefiledir/'latin1.txt'

    rwfile = ReadWriteFile(encodings=['latin1'])  # optional encoding
    text = rwfile.readAnything(oldFile)
    assert text == 'latin1 café'

# def test_latin1_cp1252_write_file(tmp_path):
#     """ TODO (QH) to be done, these encodings do not take all characters,
#     and need special attention. latin1 and cp1252 are hard to be distinguished
#     For now, cp1252 (holding more (some special characters like the euro sign and quotes))
#     is favored over latin1.
#     (as long as the "fallback" is utf-8, all write files should go well!)
#     """
#     testDir = tmp_path / testFolderName
#     testDir.mkdir()
#     _newFile = testDir/ 'latin1.txt'
#     _newFile = testDir/'cp1252.txt'
#     assert False, "QH TODO"


def test_read_write_file(tmp_path):
    listdir, join, splitext = os.listdir, os.path.join, os.path.splitext
    testDir = tmp_path / testFolderName
    testDir.mkdir()
    mock_files_list=listdir(mock_readwritefiledir)
    assert len(mock_files_list) > 0

    for F in mock_files_list:
        encodings = None
        if F.startswith('nsapps'):
            encodings = ['utf-16le']
            continue    # utf16-le is not caught by the standard function, but needs its own encoding
        if not F.startswith('output-'):
            Fout = 'output-' + F
            #read the file from the mock folder
            F_path =   mock_readwritefiledir / F
            rwfile = ReadWriteFile(encodings=encodings)
            text = rwfile.readAnything(F_path)
            trunk, _ext = splitext(F)
            Fout = trunk + ".txt"
            Fout_path = testDir/ Fout
            #write to our temp folder
            rwfile.writeAnything(Fout_path, text)
            #make sure they are the same
            org = open(F_path, 'rb').read()
            new = open(Fout_path, 'rb').read()
            for i, (o,n) in enumerate(zip(org, new)):
                if o != n:
                    parto = org[i:i+2]
                    partn = new[i:i+2]
                    raise ValueError(f'old: "{F_path}", new: "{Fout_path}", differ at pos {i}: Old: "{o}", new: "{n}", partold (i:i+2): "{parto}", partnew: "{partn}"')

def test_acoustics_ini(tmp_path):
    """this is a utf-8 file with a bom mark. Try also writing back!
    """
    testDir = tmp_path / testFolderName
    testDir.mkdir()


    F='acoustic.ini'
    F_path = mock_readwritefiledir/F
    rwfile = ReadWriteFile()
    config_text = rwfile.readAnything(F_path)
    Config = configparser.ConfigParser()
    Config.read_string(config_text)
    assert Config.get('Acoustics', '2 2') == '2_2'
    
    newFile1 = 'output1' + F
    newPath1 = testDir/newFile1
    rwfile.writeAnything(newPath1, config_text)
    
    assert filecmp.cmp(F_path, newPath1)
    
    rwfile2 = ReadWriteFile() 
    text2 = rwfile2.readAnything(newPath1)
    bom2 = rwfile2.bom
    encoding2 = rwfile2.encoding

    tRaw = rwfile.rawText
    tRaw2 = rwfile2.rawText

    assert tRaw2 == tRaw
    assert text2[0:5] == '[Base'
    assert bom2 == [239, 187, 191]
    assert encoding2 == 'utf-8'
    
    



@pytest.mark.parametrize("F", ['originalnatlink.ini', 'natlinkconfigured.ini'])
def test_config_ini(tmp_path,F):
    F_path = mock_readwritefiledir/ F
    testDir = tmp_path / testFolderName
    testDir.mkdir()
    rwfile = ReadWriteFile()
    config_text = rwfile.readAnything(F_path)
    Config = configparser.ConfigParser()
    Config.read_string(config_text)
    debug_level = Config.get('settings', 'log_level')
    assert debug_level == 'DEBUG'
    Config.set('settings', 'log_level', 'INFO')
    new_debug_level = Config.get('settings', 'log_level')
    assert new_debug_level == 'INFO'
    Fout_path = testDir/F
    Config.write(open(Fout_path, 'w', encoding=rwfile.encoding))



if __name__ == "__main__":
    pytest.main(['test_readwritefile.py'])
    