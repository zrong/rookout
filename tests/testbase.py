import os
import shutil
import ftplib
from zrong import base

workDir = None

class TestDictBase:
    def __init__(self):
        super(TestDictBase, self).__init__()
        self._dict = base.DictBase({"name":"neo", "sex":"unknown"})

    def test_getattr(self):
        self._dict.name;

    def test_setattr(self):
        self._dict.name = "zrong";

    def test_delattr(self):
        del self._dict.name

    def test_dump(self):
        self._dict.dump()

    def test_copy_from_dict(self):
        nestedDict = dict(
                a = 1,
                b = {'bb':{'bbb':{'bbbb':2}}},
                )
        newDict = base.DictBase()
        newDict.copy_from_dict(nestedDict)
        assert newDict.a == 1 and newDict.b.bb.bbb.bbbb == 2

    def test_save_to_file(self):
        fileName = "__TEST_DICT_BASE_WRITE_TO_FILE__.py"
        filePath =  os.path.join(workDir, fileName)
        self._dict.save_to_file(filePath)
        os.remove(filePath)

def setup():
    global workDir
    workDir = os.path.split(os.path.abspath(__file__))[0]

def test_list_dir():
    assert len(list(base.list_dir(workDir))) > 0

def test_copy_dir():
    dirName = "__TEST_COPY_DIR__"
    dstPath = os.path.join(workDir, dirName)
    souPath = os.path.join(workDir, os.pardir, 'zrong')
    base.copy_dir(souPath, dstPath, True)
    shutil.rmtree(dstPath)

def test_get_files():
    assert len(list(base.get_files(workDir))) > 0

def test_read_file():
    base.read_file(__file__)

def test_write_file():
    fileName = "__TEST_WRITE_FILE__.txt"
    filePath =  os.path.join(workDir, fileName)
    base.write_file(filePath, filePath)
    os.remove(filePath)

def test_get_md5():
    assert len(base.get_md5(__file__)) == 32

def test_get_ftp():
    ftpobj = base.get_ftp({
            'server':'127.0.0.1',
            'user':'user',
            'password':'password',
        })[0]
    print(ftpobj)
    assert isinstance(ftpobj, ftplib.FTP)
