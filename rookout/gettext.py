#########################################
# gettext.py
#
# Author zrong(zengrong.net)
# Creation 2015-03-04
# Last Editing 2015-06-14
#########################################

"""
.. module:: gettext
   :platform: Unix, Windows
   :synopsis: 调用外部的 gettext 工具链。

.. moduleauthor:: zrong(zengrong.net)

"""

import os
import subprocess
import tempfile
from rookout import slog

class Gettext(object):
    """创建一个对象保存 gettext 的相关配置。

    """ 
    def __init__(self, is_windows=False, binpath=None):
        if is_windows:
            self._xgettext = os.path.join(binpath, "xgettext.exe")
            self._msgfmt = os.path.join(binpath, "msgfmt.exe")
            self._msgmerge = os.path.join(binpath, "msgmerge.exe")
        else:
            self._xgettext = "xgettext"
            self._msgfmt = "msgfmt"
            self._msgmerge = "msgmerge"

    def merge(self, po_file, source_files):
        """从源码中获取所有条目，合并到 po_file 中。

        :param string po_file: 待写入的 po 文件路径。
        :param list source_files :  所有待处理的原文件路径 list。

        """
        # Create a temporary file to write pot file
        pot_file = tempfile.NamedTemporaryFile(mode='wb', prefix='rookout_', delete=False)
        pot_filename = pot_file.name
        slog.info('Create POT file [%s].', pot_filename)
        xargs = [self._xgettext,
                "--package-name=main",
                "--package-version=0.1",
                "--default-domain=main",
                "--from-code=UTF-8",
                "-C", "-k_",
                "--output", pot_filename]
        txt = subprocess.check_output(xargs+source_files, 
                stderr=subprocess.STDOUT, 
                universal_newlines=True)
        if len(txt) > 0:
            raise(ChildProcessError(txt))
        slog.info('Start merge [%s] to [%s].', pot_filename, po_file)
        xargs = [self._msgmerge, "-U", po_file, pot_filename]
        txt = subprocess.check_output(xargs, universal_newlines=True)
        slog.info(txt)
        pot_file.close()
        os.remove(pot_filename)

    def fmt(self, po_file, mo_file):
        """将 po 文件转换成 mo 文件。

        :param string po_file: 待转换的 po 文件路径。
        :param string mo_file: 目标 mo 文件的路径。

        """
        if not os.path.exists(po_file):
            slog.error('The PO file [%s] is non-existen!'%po_file)
            return
        txt = subprocess.check_output([self._msgfmt, 
            '--check', "--strict", '--verbose', 
            "--output-file", mo_file, po_file], 
                stderr=subprocess.STDOUT, 
                universal_newlines=True)
        slog.info(txt)

