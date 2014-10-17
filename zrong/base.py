# base.py
# Author zrong
# Creation 2014-09-23

import os
import logging
from string import Template

# log for system debug
slog = logging.getLogger("system")
__LOG_FMT = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s\n")

class DictBase(dict):
    def __missing__(self, key):
        return None

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value
        
    def __delattr__(self, name):
        del self[name]

    def copyFromDict(self, adict, parent=None):
        if not parent:
            parent = self
        for k,v in adict.items():
            if isinstance(v, dict):
                vDict = DictBase(v)
                self.copyFromDict(v, vDict)
                parent[k] = vDict
            else:
                parent[k] = v

    def dump(self, human=False):
        txt = str(self)
        if human:
            txt = txt.replace(", '", ",\n'")
            txt = txt.replace("{", "{\n")
            txt = txt.replace("}", "\n}")
            txt = txt.replace("[", "[\n")
            txt = txt.replace("]", "\n]")
        return txt

    def saveToFile(self, path, human=True):
        writeFile(path, self.dump(human))
        slog.info("Save %a done.", path)

    def readFromFile(self, path):
        if not os.path.exists(path):
            slog.warning("The file %s is not exist.", path)
            return False
        txt = readFile(path)
        dic = eval(txt)
        self.copyFromDict(dic)
        return True

def addLoggerHandler(log, handler=None, debug=None, fmt=None):
    if debug:
        log.setLevel(debug)
    if handler:
        # if not fmt:
        #     fmt = __LOG_FMT
        # handler.setFormatter(fmt)
        log.addHandler(handler)

def listDir(sou_dir, include_root=None, include_file=True):
    new_list = []
    for cur_file in os.listdir(sou_dir):
        if cur_file.lower() == ".ds_store":
            continue
        path_with_root = os.path.join(sou_dir, cur_file)
        if include_file or os.path.isdir(path_with_root):
            if include_root:
                new_list.append(path_with_root)
            else:
                new_list.append(cur_file)
    return new_list

def getFiles(path, ext=[], include=True):
    has_ext = len(ext)>0
    for p, d, fs in os.walk(path):
        for f in fs:
            if has_ext:
                in_ext = False
                for name in ext:
                    if f.endswith(name):
                        in_ext = True
                        break
                if (include and in_ext) or \
                (not include and not in_ext):
                    yield os.path.join(p,f)
            else:
                yield os.path.join(p, f)

def readFile(filePath):
    with open(filePath, mode="r",encoding="utf-8") as afile:
        txt = afile.read()
    return txt

def writeFile(filePath, txt):
    if not os.path.exists(filePath):
        upDir = os.path.dirname(filePath)
        if not os.path.isdir(upDir):
            os.makedirs(upDir)

    with open(filePath, mode="w",encoding="utf-8") as afile:
        afile.write(txt)

def writeByTempl(templ, target, sub_value):
    templ_txt = readFile(templ)
    writeFile(target, Template(templ_txt).substitute(sub_value))
