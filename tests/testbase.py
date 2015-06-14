import os
import shutil
from rookout import base

workDir = None

def setup():
    global workDir
    workDir = os.path.split(os.path.abspath(__file__))[0]

def test_list_dir():
    assert len(list(base.list_dir(workDir))) > 0

def test_copy_dir():
    dirName = "__TEST_COPY_DIR__"
    dstPath = os.path.join(workDir, dirName)
    souPath = os.path.join(workDir, os.pardir, 'rookout')
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

