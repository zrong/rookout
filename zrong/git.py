# git.py
# Creation 2014-10-23
# Author zrong

"""
.. module:: git
   :platform: Unix, Windows
   :synopsis: git 通用操作。

.. moduleauthor:: zrong(zengrong.net)

"""

import os
import subprocess
from .base import slog

def getArgs(path, *args):
    """获取可被 subprogress 执行的 git 参数 list。

    :param str path: git 仓库文件夹路径。
    :param \*args: git 的附加参数。

    """
    base = [ 'git' ]
    if path:
        base.append("--git-dir="+os.path.join(path, ".git"))
        base.append("--work-tree="+path)
    for arg in args:
        base.append(arg)
    return base

def getHash(path, cut=0):
    """获取可被 git 的 HEAD 的 sha1 值。

    :param str path: git 仓库文件夹路径。
    :param int cut: 包含的 sha1 值的长度。0代表不剪切。
    :returns: 剪切过的 sha1 的值。
    :rtype: str

    """
    arg = getArgs(path, 'rev-parse', 'HEAD')
    # maybe the string is with a linebreak.
    sha1 = subprocess.check_output(arg, universal_newlines=True).strip()
    if cut > 0:
        sha1 = sha1[:7]
    return sha1

def getCommitTimes(path):
    """获取提交次数。

    :param str path: git 仓库文件夹路径。
    :returns: 包含所有分支的提交次数。
    :rtype: int

    """
    arg = getArgs(path, "rev-list", '--all')
    output = subprocess.check_output(arg, universal_newlines=True)
    return output.count("\n")

def updateSubmodules(path, init=True, update=True):
    """更新子模块。

    :param str path: git 仓库文件夹路径。
    :param bool init: 是否初始化子模块。
    :param bool update: 是否更新子模块。

    """
    succ = None
    if init:
        arg = getArgs(path, 'submodule', 'init')
        slog.info(' '.join(arg))
        succ = subprocess.call(arg)
        if succ>0:
            slog.error('git execute error!')
            return succ
    if update:
        arg = getArgs(path, "submodule", "update")
        slog.info(' '.join(arg))
        succ = subprocess.call(arg)
        if succ>0:
            slog.error('git execute error!')
            return succ
    return succ
