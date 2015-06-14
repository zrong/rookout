import os
from rookout.conf import (PYConf, INIConf)

workDir = os.path.split(os.path.abspath(__file__))[0]

# setup is called behind TestPYConf and TestINIConf
# def setup():
#     global workDir
#     workDir = os.path.split(os.path.abspath(__file__))[0]
#     print('setup', workDir)

class TestPYConf(object):
    def __init__(self):
        self._dict = PYConf({"name":"neo", "sex":"unknown"})

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
        newDict = PYConf()
        newDict.copy_from_dict(nestedDict)
        assert newDict.a == 1 and newDict.b.bb.bbb.bbbb == 2

    def test_save_to_file(self):
        # print('test_save_to_file', workDir)
        fileName = "__TEST_DICT_BASE_WRITE_TO_FILE__.py"
        filePath =  os.path.join(workDir, fileName)
        self._dict.save_to_file(filePath)
        os.remove(filePath)

class TestINIConf(object):
    def __init__(self):
        self._conf = INIConf()
        self._conf.read(os.path.join(workDir, 'config.ini'))

    def test_lists(self):
        assert len(self._conf.lists()) == 1

    def test_list(self):
        assert self._conf.list('tt')
        assert self._conf.list('@list tt')

