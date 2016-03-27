#########################################
# base.py
#
# Author zrong
# Creation 2014-09-23
# Last Editing 2015-06-14
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
from rookout import slog

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

def read_file(file_path, **kws):
    """读取文本文件的内容。

    :param str file_path: 文件路径。
    :returns: 文件内容。
    :rtype: str

    """
    kw = {"mode":"r", "encoding":"utf-8"}
    if kws:
        for k,v in kws.items():
            kw[k] = v
    with open(file_path, **kw) as afile:
        txt = afile.read()
    return txt

def write_file(file_path, txt, **kws):
    """将文本内容写入文件。

    :param str file_path: 文件路径。
    :param str txt: 待写入的文件内容。

    """
    if not os.path.exists(file_path):
        upDir = os.path.dirname(file_path)
        if not os.path.isdir(upDir):
            os.makedirs(upDir)

    kw = {"mode":"w", "encoding":"utf-8"}
    if kws:
        for k,v in kws.items():
            kw[k] = v
    with open(file_path, **kw) as afile:
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
    raise FileNotFoundError("Error when get md5 for %s!"%path)

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

    :param str fmt: 要检测测字符串形式，例如 rookout-%s.tar.gz ，其中 %s 会被正则替换。
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

def merge_dicts(d1, d2):
    """合并两个无限深度的 dict
    会自动合并 list 格式

    :param dict d1: 被合并的 dict
    :param dict d2: 待合并的 dict
    :returns: 一个新的生成器对象
    :rtype: generator

    """
    for k in set(d1.keys()).union(d2.keys()):
        if k in d1 and k in d2:
            if isinstance(d1[k], dict) and isinstance(d2[k], dict):
                yield (k, dict(merge_dicts(d1[k], d2[k])))
            elif isinstance(d1[k], list):
                if isinstance(d2[k], list):
                    d1[k].extend(d2[k])
                else:
                    d1[k].append(d2[k])
                yield(k, d1)
            else:
                # If one of the values is not a dict, you can't continue merging it.
                # Value from second dict overrides one in first and we move on.
                yield (k, d2[k])
                # Alternatively, replace this with exception raiser to alert you of value conflicts
        elif k in d1:
            yield (k, d1[k])
        else:
            yield (k, d2[k])

