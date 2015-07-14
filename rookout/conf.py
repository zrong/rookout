########################################
# conf.py
# Author zrong(zengrong.net)
#
# Creation 2015-06-14
# Last Editing 2015-06-14
########################################

"""
.. module:: conf
   :platform: Unix, Windows
   :synopsis: 对配置文件的封装。

.. moduleauthor:: zrong(zengrong.net)

"""

import os
import re
from rookout import slog
from rookout.base import (read_file, write_file)
from configparser import (ConfigParser, NoSectionError)

class PYConf(dict):
    """基于 Python dict 的配置文件。

    dict 默认不适合当作配置文件对象使用。如要有下面几点不便：
    
    #. 对于不存在的 key，会 raise KeyError 错误；
    #. dict不能使用 ``.`` 语法访问。

    :class:`rookout.PYConf` 解决了这些问题，还另外提供了一些方法在使用上更加方便。

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
        :type parent: rookout.PYConf

        """
        if not parent:
            parent = self
        for k,v in adict.items():
            if isinstance(v, dict):
                vDict = PYConf(v)
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

class INIConf(ConfigParser):
    """对 INI 格式的配置文件做了一些变化，使其可以支持列表。

    只需要将 section 的名称设置为 [@list name] 即可加入一个名称为 name 的 section。

    这个 sectioni 中的每一行都作为列表的一项。
    """ 

    _LIST_TMPL = r"""
        @(list)?                            # @ or @list
        \s*(?P<header>\w+)                  # very permissive!
        """
    
    LISTCRE = re.compile(_LIST_TMPL, re.VERBOSE)

    def __init__(self):
        # Only use the '=' as a delimiter
        super().__init__(allow_no_value=True, delimiters=('='))

    # override RawConfigParser to protect case.
    def optionxform(self, optionstr):  
        return optionstr

    def _get_list_name(self, section):
        if not self.LISTCRE.match(section):
            section = "@list "+section
        return section

    def has_list(self, section):
        return self.has_section(self._get_list_name(section))

    def list(self, section):
        return self.options(self._get_list_name(section))

    def lists(self):
        list_sections = []
        for name in self.sections():
            m = self.LISTCRE.search(name)
            if m:
                list_sections.append(m.group('header'))
        return list_sections

def merge_INIConf(a, b):
    """用 b 的内容覆盖 a 的内容（若重名），并返回 a
    """
    for sname in b.sections():
        if a.has_section(sname):
            for oname in b.options(sname):
                a[sname][oname] = b[sname][oname]
        else:
            a[sname] = b[sname]
    return a
