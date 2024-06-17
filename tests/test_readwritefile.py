
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
    newFile = testDir/"outut-accented.txt"
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

    oldFile = mock_readwritefiledir/'latin1 accented.txt'

    rwfile = ReadWriteFile(encodings=['latin1'])  # optional encoding
    text = rwfile.readAnything(oldFile)
    assert text == 'latin1 café'
    
    
def test_nsapps_utf16(tmp_path):
    """try the encodings from the nsapps ini file, version of Aaron
    """
    testDir = tmp_path / testFolderName
    testDir.mkdir()
    # file_in = 'nsapps_aaron.ini'
    file_in = 'nsapps_aaron.ini'
    oldFile = mock_readwritefiledir/file_in
    rwfile = ReadWriteFile(encodings=['utf-16le', 'utf-16be', 'utf-8'])  # optional encoding
    text = rwfile.readAnything(oldFile)
    bom = rwfile.bom
    encoding = rwfile.encoding
    assert text[0] == ';' 
 
    assert bom == [255, 254]
    assert encoding == 'utf-16le'
    
    
    newFile1 = 'output1' + file_in
    newPath1 = testDir/newFile1
    rwfile.writeAnything(newPath1, text)
    
    assert filecmp.cmp(oldFile, newPath1)
    
    rwfile2 = ReadWriteFile(encodings=['utf-16le'])  # optional encoding
    text2 = rwfile2.readAnything(newPath1)
    bom2 = rwfile2.bom
    encoding2 = rwfile2.encoding

    tRaw = rwfile.rawText
    tRaw2 = rwfile2.rawText

    assert text2[0] == ';'
    assert bom2 == [255, 254]
    assert encoding2 == 'utf-16le'

def test_latin1_cp1252_write_file(tmp_path):
    testDir = tmp_path / testFolderName
    testDir.mkdir()
    _newFile = testDir/ 'latin1.txt'
    _newFile = testDir/'cp1252.txt'
    assert False, "QH TODO"

    # TODO (QH) to be done, these encodings do not take all characters,
    # and need special attention.
    # (as long as the "fallback" is utf-8, all write files should go well!)

def test_read_write_file(tmp_path):
    listdir, join, splitext = os.listdir, os.path.join, os.path.splitext
    testDir = tmp_path / testFolderName
    testDir.mkdir()
    mock_files_list=listdir(mock_readwritefiledir)
    assert len(mock_files_list) > 0

    for F in mock_files_list:
        if not F.startswith('output-'):
            Fout = 'output-' + F
            #read the file from the mock folder
            F_path =   mock_readwritefiledir / F
            rwfile = ReadWriteFile()
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
    F='acoustic.ini'
    F_path = mock_readwritefiledir/F
    rwfile = ReadWriteFile()
    config_text = rwfile.readAnything(F_path)
    Config = configparser.ConfigParser()
    Config.read_string(config_text)
    assert Config.get('Acoustics', '2 2') == '2_2' 

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
    