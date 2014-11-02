from zrong import base
import os

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

    def test_copyFromDict(self):
        nestedDict = dict(
                a = 1,
                b = {'bb':{'bbb':{'bbbb':2}}},
                )
        newDict = base.DictBase()
        newDict.copyFromDict(nestedDict)
        assert newDict.a == 1 and newDict.b.bb.bbb.bbbb == 2

    def test_saveToFile(self):
        fileName = "__TEST_DICT_BASE_WRITE_TO_FILE__.py"
        filePath =  os.path.join(workDir, fileName)
        self._dict.saveToFile(filePath)
        os.remove(filePath)


def setup():
    global workDir
    workDir = os.path.split(os.path.abspath(__file__))[0]

def test_listDir():
    assert len(list(base.listDir(workDir))) > 0

def test_getFiles():
    assert len(list(base.getFiles(workDir))) > 0

def test_readFile():
    base.readFile(__file__)

def test_writeFile():
    fileName = "__TEST_WRITE_FILE__.txt"
    filePath =  os.path.join(workDir, fileName)
    base.writeFile(filePath, filePath)
    os.remove(filePath)

def test_getMD5():
    assert len(base.getMD5(__file__)) == 32
