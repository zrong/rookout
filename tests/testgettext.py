import os
from rookout.gettext import Gettext
from rookout.base import get_files

gt = None
workdir = None
src = '/Volumes/HD1/works/yhq/client/src/game'

def setup():
    global workdir, gt
    workdir = os.path.split(os.path.abspath(__file__))[0]
    gt = Gettext()

def test_merge():
    lua_files = list(get_files(src, ext=['.lua']))
    po_file = os.path.join(workdir, 'zh_cn.po')
    gt.merge(po_file, lua_files)

def test_fmt():
    po_file = os.path.join(workdir, 'zh_cn.po')
    mo_file = os.path.join(workdir, 'zh_cn.mo')
    gt.fmt(po_file, mo_file)
