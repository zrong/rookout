# base.py
# Author zrong
# Creation 2014-09-23
# Last Editing 2014-11-02

"""
.. module:: base
   :platform: Unix, Windows
   :synopsis: 一些通用功能的封装。

.. moduleauthor:: zrong(zengrong.net)

"""

import os
import shutil
import logging
import hashlib
import ftplib
from string import Template


slog = logging.getLogger("system")
"""默认的系统 log。"""

__LOG_FMT = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s\n")


class DictBase(dict):
    """作为配置文件的基类。

    dict 默认不适合当作配置文件对象使用。如要有下面几点不便：
    
    #. 对于不存在的 key，会 raise KeyError 错误；
    #. dict不能使用 ``.`` 语法访问。

    :class:`DictBase` 解决了这些问题，还另外提供了一些方法在使用上更加方便。

    """ 

    def __missing__(self, key):
        return None

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value
        
    def __delattr__(self, name):
        del self[name]

    def copy_from_dict(self, adict, parent=None):
        """从一个已经存在的 dict 中复制所有的值。

        :param adict: 被复制的 dict。
        :type adict: dict
        :param parent:  复制到哪个父对象。
                        若为 None 则复制到 self 。
        :type parent: DictBase

        """
        if not parent:
            parent = self
        for k,v in adict.items():
            if isinstance(v, dict):
                vDict = DictBase(v)
                self.copy_from_dict(v, vDict)
                parent[k] = vDict
            else:
                parent[k] = v

    def dump(self, human=False):
        """将自身内容打印成字符串

        :param bool human: 若值为 True ，则打印成易读格式。

        """
        txt = str(self)
        if human:
            txt = txt.replace(", '", ",\n'")
            txt = txt.replace("{", "{\n")
            txt = txt.replace("}", "\n}")
            txt = txt.replace("[", "[\n")
            txt = txt.replace("]", "\n]")
        return txt

    def save_to_file(self, path, human=True):
        """将自身内容保存到文件。

        :param str path: 保存的文件路径。
        :param bool human: 参见 :func:`dump()`

        """
        write_file(path, self.dump(human))
        slog.info("Save %a done.", path)

    def read_from_file(self, path):
        """从一个文本文件中读入信息。
        假设该文本文件的格式与 :func:`dump()` 相同。

        :param str path: 待读入的文件路径。

        """
        if not os.path.exists(path):
            slog.warning("The file %s is not exist.", path)
            return False
        txt = read_file(path)
        dic = eval(txt)
        self.copy_from_dict(dic)
        return True

    copyFromDict = copy_from_dict
    saveToFile = save_to_file
    readFromFile = read_from_file


class ZrongError(Exception):
    """zrong 模块使用的异常类。"""
    pass


def add_log_handler(log, handler=None, debug=None, fmt=None):
    """为一个 :class:`logging.Logger` 的实例增加 handler。

    :param Logger log: 需要处理的 :class:`logging.Logger` 的实例。
    :param Handler handler: 一个 :class:`logging.Handler` 的实例。
    :param int debug: Debug 级别。
    :param str fmt: Handler 的 Formatter。

    """
    if debug:
        log.setLevel(debug)
    if handler:
        # if not fmt:
        #     fmt = __LOG_FMT
        if fmt:
            handler.setFormatter(fmt)
        log.addHandler(handler)

def list_dir(sourceDir, includeSource=None, includeFile=True):
    """与 :func:`os.listdir()` 类似，但提供一些筛选功能，且返回生成器对象。

    :param str sourceDir: 待处理的文件夹。
    :param bool includeSource: 遍历结果中是否包含源文件夹的路径。
    :param bool includeFile:    是否包含文件。True 表示返回的内容中既包含文件，又
                                包含文件夹；Flase 代表仅包含文件夹。
    :return: 一个生成器对象。

    """
    for cur_file in os.listdir(sourceDir):
        if cur_file.lower() == ".ds_store":
            continue
        pathWithSource = os.path.join(sourceDir, cur_file)
        if includeFile or os.path.isdir(pathWithSource):
            if includeSource:
                yield pathWithSource
            else:
                yield cur_file

def copy_dir(souDir, dstDir, delDst=False):
    """:func:`shutil.copytree()` 也能实现类似功能，
    但前者要求目标文件夹必须不存在。
    而 copy_dir 没有这个要求，它可以将 souDir 中的文件合并到 dstDir 中。

    :param str souDir: 待复制的文件夹；
    :param str dstDir: 目标文件夹；
    :param bool delDst: 是否删除目标文件夹。

    """
    if delDst and os.path.isdir(delDst):
        shutil.rmtree(dstDir)
    os.makedirs(dstDir, exist_ok=True)
    for cur_file in list_dir(souDir):
        dst_file = os.path.join(dstDir, cur_file)
        cur_file = os.path.join(souDir, cur_file)
        if os.path.isdir(cur_file):
            os.makedirs(dst_file, exist_ok=True)
            copy_dir(cur_file, dst_file)
        else:
            shutil.copyfile(cur_file, dst_file)

def get_files(path, ext=[], include=True):
    """遍历提供的文件夹的所有子文件夹，饭后生成器对象。

    :param str path: 待处理的文件夹。
    :param list ext: 扩展名列表。
    :param bool include:    若值为 True，代表 ext 提供的是包含列表；
                            否则是排除列表。
    :returns: 一个生成器对象。 

    """
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

def read_file(filePath):
    """读取文本文件的内容。

    :param str filePath: 文件路径。
    :returns: 文件内容。
    :rtype: str

    """
    with open(filePath, mode="r",encoding="utf-8") as afile:
        txt = afile.read()
    return txt

def write_file(filePath, txt):
    """将文本内容写入文件。

    :param str filePath: 文件路径。
    :param str txt: 待写入的文件内容。

    """
    if not os.path.exists(filePath):
        upDir = os.path.dirname(filePath)
        if not os.path.isdir(upDir):
            os.makedirs(upDir)

    with open(filePath, mode="w",encoding="utf-8") as afile:
        afile.write(txt)

def write_by_templ(templ, target, subValue, safe=False):
    """根据模版写入文件。

    :param str templ: 模版文件所在路径。
    :param str target: 要写入的文件所在路径。
    :param dict subValue: 被替换的内容。

    """
    templ_txt = read_file(templ)
    txt = None
    if safe:
        txt = Template(templ_txt).safe_substitute(subValue)
    else:
        txt = Template(templ_txt).substitute(subValue)
    write_file(target, txt)

def get_md5(path):
    """获取文件的 MD5 值。

    :param str path: 文件路径。
    :returns: MD5 值。
    :rtype: str

    """
    with open(path,'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        return md5obj.hexdigest()
    raise ZrongError("Error when get md5 for %s!"%path)

def get_ftp(ftpConf, debug=0):
    """得到一个 已经打开的FTP 实例，和一个 ftp 路径。

    :param str ftpConf: ftp配置文件，格式如下：
    
        >>> {
        >>>     'server':'127.0.0.1',
        >>>     'start_path':None,
        >>>     'user':'admin',
        >>>     'password':'123456',
        >>> }

    :returns: ftp, ftpserverstr
    :rtype: :class:`ftplib.FTP` , str

    """
    server = ftpConf.get('server')
    user = ftpConf.get('user')
    password = ftpConf.get('password')
    start_path = ftpConf.get('start_path')
    slog.info("Connecting FTP server %s ......", server)
    ftpStr = 'ftp://%s/'%server
    if start_path:
        ftpStr = ftpStr+start_path
    ftp = ftplib.FTP(server, user, password)
    ftp.set_debuglevel(debug)
    if start_path:
        ftp.cwd(start_path)
    serverFiles = ftp.nlst()
    slog.info('There are some files in %s:\n[%s]'%(ftpStr, ', '.join(serverFiles)))
    return ftp, ftpStr


getMD5          = get_md5
writeByTempl    = write_by_templ
writeFile       = write_file
listDir         = list_dir
addLoggerHandler = add_log_handler
copyDir         = copy_dir
getFiles        = get_files
readFile        = read_file
