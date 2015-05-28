#########################################
# base.py
#
# Author zrong
# Creation 2014-09-23
# Last Editing 2015-01-30
#########################################

"""
.. module:: base
   :platform: Unix, Windows
   :synopsis: 一些通用功能的封装。

.. moduleauthor:: zrong(zengrong.net)

"""

import os
import re
import sys
import zipfile
import shutil
import hashlib
import tempfile
from string import Template
from zrong import slog


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


def list_dir(sourceDir, include_source=None, include_file=True):
    """与 :func:`os.listdir()` 类似，但提供一些筛选功能，且返回生成器对象。

    :param str sourceDir: 待处理的文件夹。
    :param bool include_source: 遍历结果中是否包含源文件夹的路径。
    :param bool include_file:    是否包含文件。True 表示返回的内容中既包含文件，又
                                包含文件夹；Flase 代表仅包含文件夹。
    :return: 一个生成器对象。

    """
    for cur_file in os.listdir(sourceDir):
        if cur_file.lower() == ".ds_store":
            continue
        pathWithSource = os.path.join(sourceDir, cur_file)
        if include_file or os.path.isdir(pathWithSource):
            if include_source:
                yield pathWithSource
            else:
                yield cur_file

def copy_dir(sou_dir, dst_dir, del_dst=False, del_subdst=False):
    """:func:`shutil.copytree()` 也能实现类似功能，
    但前者要求目标文件夹必须不存在。
    而 copy_dir 没有这个要求，它可以将 sou_dir 中的文件合并到 dst_dir 中。

    :param str sou_dir: 待复制的文件夹；
    :param str dst_dir: 目标文件夹；
    :param bool del_dst: 是否删除目标文件夹。
    :param bool del_subdst: 是否删除目标子文件夹。

    """
    if del_dst and os.path.isdir(del_dst):
        shutil.rmtree(dst_dir)
    os.makedirs(dst_dir, exist_ok=True)
    for cur_file in list_dir(sou_dir):
        dst_file = os.path.join(dst_dir, cur_file)
        cur_file = os.path.join(sou_dir, cur_file)
        if os.path.isdir(cur_file):
            if del_subdst and os.path.isdir(dst_file):
                shutil.rmtree(dst_file)
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

def read_file(file_path):
    """读取文本文件的内容。

    :param str file_path: 文件路径。
    :returns: 文件内容。
    :rtype: str

    """
    with open(file_path, mode="r",encoding="utf-8") as afile:
        txt = afile.read()
    return txt

def write_file(file_path, txt):
    """将文本内容写入文件。

    :param str file_path: 文件路径。
    :param str txt: 待写入的文件内容。

    """
    if not os.path.exists(file_path):
        upDir = os.path.dirname(file_path)
        if not os.path.isdir(upDir):
            os.makedirs(upDir)

    with open(file_path, mode="w",encoding="utf-8") as afile:
        afile.write(txt)

def write_by_templ(templ, target, sub_value, safe=False):
    """根据模版写入文件。

    :param str templ: 模版文件所在路径。
    :param str target: 要写入的文件所在路径。
    :param dict sub_value: 被替换的内容。

    """
    templ_txt = read_file(templ)
    txt = None
    if safe:
        txt = Template(templ_txt).safe_substitute(sub_value)
    else:
        txt = Template(templ_txt).substitute(sub_value)
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

def create_zip(files, trim_arcname=None, target_file=None, **zipfile_args):
    """创建一个 zip 文件。

    :param list files: 要创建zip 的文件列表。
    :param int trim_arcname: 若提供这个值，则使用 ZipFile.write(filename, filename[trim_arcname:]) 进行调用。
    :returns: zip 文件的路径。
    :rtype: str

    """
    zipname = None
    azip = None
    if not target_file:
        azip = tempfile.NamedTemporaryFile(mode='wb', delete=False)
        zipname = azip.name
    else:
        azip = target_file
        zipname = target_file.name if hasattr(azip, 'read') else azip
    slog.info('Package %d files to "%s"'%(len(files), azip.name))
    fileNum = len(files)
    curFile = 0
    zipfile_args['mode'] = 'w'
    if not zipfile_args.get('compression'):
        zipfile_args['compression'] = zipfile.ZIP_DEFLATED
    with zipfile.ZipFile(azip, **zipfile_args) as zipf:
       for f in files:
           percent = round(curFile/fileNum*100)
           sys.stdout.write('\r%d%%'%(percent))
           sys.stdout.flush()
           zipf.write(f, f[trim_arcname:] if trim_arcname else None )
           curFile = curFile+1

       sys.stdout.write('\r100%\n')
       sys.stdout.flush()

    if hasattr(azip, 'close'):
        azip.close()
    return zipname

def get_max_ver(fmt, filelist):
    """有一堆字符串，文件名均包含 %d.%d.%d 形式版本号，返回其中版本号最大的那个。
    我一般用它来检测一堆发行版中版本号最大的那个文件。

    :param str fmt: 要检测测字符串形式，例如 zrong-%s.tar.gz ，其中 %s 会被正则替换。
    :param list files: 字符串列表。
    :returns: 版本号最大的字符串。
    :rtype: str

    """
    x, y, z = 0,0,0
    verpat = fmt%'(\d+).(\d+).(\d+)'
    verre = re.compile(r''+verpat+'', re.M) 
    for f in filelist:
        match = verre.search(f)
        if match:
            x1 = int(match.group(1))
            y1 = int(match.group(2))
            z1 = int(match.group(3))
            if x1 >= x and y1 >= y:
                x = x1
                y = y1
                z = z1
    verfmt = fmt%('%d.%d.%d')
    name = verfmt%(x, y, z)
    if x == 0 and y == 0 and z == 0:
        slog.info('Can not find the string "%s" !'%name)
        return None
    return name

