# git.py
# Creation 2014-10-23
# Author zrong

import os
import subprocess
from .base import slog

def getArgs(path, *args):
    base = [ 'git' ]
    if path:
        base.append("--git-dir="+os.path.join(path, ".git"))
        base.append("--work-tree="+path)
    for arg in args:
        base.append(arg)
    return base

def getHash(path, cut=0):
    arg = getArgs(path, 'rev-parse', 'HEAD')
    sha1 = subprocess.check_output(arg, universal_newlines=True)
    if cut > 0:
        sha1 = sha1[:7]
    return sha1

def getCommitTimes(path):
    arg = getArgs(path, "rev-list", '--all')
    output = subprocess.check_output(arg, universal_newlines=True)
    return output.count("\n")

def updateSubmodules(path, init=True, update=True):
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
