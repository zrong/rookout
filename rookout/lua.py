########################################
# git.py
# port from https://github.com/SirAnthony/slpp
# Modifier zrong(zengrong.net)
#
# Creation 2014-10-23
# Last Editing 2015-06-14
########################################
"""
.. module:: lua
   :platform: Unix, Windows
   :synopsis: lua-python 解析模块。

.. moduleauthor:: zrong(zengrong.net)

"""
import re
from rookout.base import read_file

ERRORS = {
    'unexp_table': u'Unexpected structure while parsing Lua string.',
    'unexp_end_string': u'Unexpected end of string while parsing Lua string.',
    'unexp_end_table': u'Unexpected end of table while parsing Lua string.',
    'mfnumber_minus': u'Malformed number (no digits after initial minus).',
    'mfnumber_dec_point': u'Malformed number (no digits after decimal point).',
    'mfnumber_sci': u'Malformed number (bad scientific format).',
}


class Lua:
    """进行 lua 标准 table 和 python 数据之间的转换。使用 python re 模块进行解析。"""

    def __init__(self):
        self.text = ''
        self.ch = ''
        self.at = 0
        self.len = 0
        self.depth = 0
        self.space = re.compile('\s', re.M)
        self.alnum = re.compile('\w', re.M)
        self.newline = '\n'
        self.tab = '\t'

    def decode(self, text):
        if not text or type(text) is not str:
            return
        #FIXME: only short comments removed
        reg = re.compile('--.*$', re.M)
        text = reg.sub('', text, 0)
        tstart = text.find('{')
        tend = text.rfind('}')
        if tstart < 0 and tend < 0:
            self.text = text
        elif tstart < 0 or tend < 0:
            raise TypeError(ERRORS['unexp_table'])
        else:
            self.text = text[tstart:tend+1]
        self.at, self.ch, self.depth = 0, '', 0
        self.len = len(self.text)
        self.next_chr()
        result = self.value()
        return result

    def encode(self, obj):
        if not obj:
            return
        self.depth = 0
        return self.__encode(obj)

    def __encode(self, obj):
        s = ''
        tab = self.tab
        newline = self.newline
        tp = type(obj)
        if tp is str:
            s += '"%s"' % obj.replace(r'"', r'\"')
        elif tp in [int, float, complex]:
            s += str(obj)
        elif tp is bool:
            s += str(obj).lower()
        elif tp in [list, tuple, dict]:
            self.depth += 1
            if len(obj) == 0 or ( tp is not dict and len(list(filter(
                    lambda x:  type(x) in (int,  float) \
                    or (type(x) is str and len(x) < 10),  obj
                ))) == len(obj) ):
                newline = tab = ''
            dp = tab * self.depth
            s += "%s{%s" % (tab * (self.depth - 2), newline)
            if tp is dict:
                s += (',%s' % newline).join(
                    [self.__encode(v) if type(k) is int \
                        else dp + '["%s"] = %s' % (k, self.__encode(v)) \
                        for k, v in obj.items()
                    ])
            else:
                s += (',%s' % newline).join(
                    [dp + self.__encode(el) for el in obj])
            self.depth -= 1
            s += "%s%s}" % (newline, tab * self.depth)
        return s

    def white(self):
        while self.ch:
            if self.space.match(self.ch):
                self.next_chr()
            else:
                break

    def next_chr(self):
        if self.at >= self.len:
            self.ch = None
            return None
        self.ch = self.text[self.at]
        self.at += 1
        return True

    def value(self):
        self.white()
        if not self.ch:
            return
        if self.ch == '{':
            return self.object()
        if self.ch == "[":
            self.next_chr()
        if self.ch in ['"',  "'",  '[']:
            return self.string(self.ch)
        if self.ch.isdigit() or self.ch == '-':
            return self.number()
        return self.word()

    def string(self, end=None):
        s = ''
        start = self.ch
        if end == '[':
            end = ']'
        if start in ['"',  "'",  '[']:
            while self.next_chr():
                if self.ch == end:
                    self.next_chr()
                    if start != "[" or self.ch == ']':
                        return s
                if self.ch == '\\' and start == end:
                    self.next_chr()
                    if self.ch != end:
                        s += '\\'
                s += self.ch
        slog.error(ERRORS['unexp_end_string'])

    def object(self):
        o = {}
        k = ''
        idx = 0
        numeric_keys = False
        self.depth += 1
        self.next_chr()
        self.white()
        if self.ch and self.ch == '}':
            self.depth -= 1
            self.next_chr()
            return o #Exit here
        else:
            while self.ch:
                self.white()
                if self.ch == '{':
                    o[idx] = self.object()
                    idx += 1
                    continue
                elif self.ch == '}':
                    self.depth -= 1
                    self.next_chr()
                    if k:
                       o[idx] = k
                    if not numeric_keys and len([ key for key in o if type(key) in (str,  float,  bool,  tuple)]) == 0:
                        ar = []
                        for key in o:
                           ar.insert(key, o[key])
                        o = ar
                    return o #or here
                else:
                    if self.ch == ',':
                        self.next_chr()
                        continue
                    else:
                        k = self.value()
                        if self.ch == ']':
                            numeric_keys = True
                            self.next_chr()
                    self.white()
                    if self.ch == '=':
                        self.next_chr()
                        self.white()
                        o[k] = self.value()
                        idx += 1
                        k = ''
                    elif self.ch == ',':
                        self.next_chr()
                        self.white()
                        o[idx] = k
                        idx += 1
                        k = ''
        slog.error(ERRORS['unexp_end_table']) #Bad exit here

    def word(self):
        s = ''
        if self.ch != '\n':
          s = self.ch
        while self.next_chr():
            if self.alnum.match(self.ch):
                s += self.ch
            else:
                if re.match('^true$', s, re.I):
                    return True
                elif re.match('^false$', s, re.I):
                    return False
                elif s == 'nil':
                    return None
                return str(s)

    def number(self):
        def next_digit(err):
            n = self.ch
            self.next_chr()
            if not self.ch or not self.ch.isdigit():
                raise TypeError(err)
            return n
        n = ''
        try:
            if self.ch == '-':
                n += next_digit(ERRORS['mfnumber_minus'])
            n += self.digit()
            if n == '0' and self.ch in ['x', 'X']:
                n += self.ch
                self.next_chr()
                n += self.hex()
            else:
                if self.ch and self.ch == '.':
                    n += next_digit(ERRORS['mfnumber_dec_point'])
                    n += self.digit()
                if self.ch and self.ch in ['e', 'E']:
                    n += self.ch
                    self.next_chr()
                    if not self.ch or self.ch not in ('+', '-'):
                        raise TypeError(ERRORS['mfnumber_sci'])
                    n += next_digit(ERRORS['mfnumber_sci'])
                    n += self.digit()
        except TypeError as e:
            slog.error(e)
            return 0
        try:
            return int(n, 0)
        except:
            pass
        return float(n)

    def digit(self):
        n = ''
        while self.ch and self.ch.isdigit():
            n += self.ch
            self.next_chr()
        return n

    def hex(self):
        n = ''
        while self.ch and \
            (self.ch in 'ABCDEFabcdef' or self.ch.isdigit()):
            n += self.ch
            self.next_chr()
        return n


lua = Lua()
"""一个默认的 lua 模块"""

def decode_file(luafile):
    """将 lua文件 解析成 python 对象。
    将 luafile 解析成字符串，然后调用 :func:`rookout.lua.decode()` 。

    :param str luafile: lua文件路径。
    :return: python 对象
    :raise: :class:`TypeError`

    """
    luastr = read_file(luafile)
    return decode(luastr)

def decode(text):
    """将 lua 解析成 python 对象。
    text 可以是标准的 lua 字符串、或者直接是一个对象。

    下面的代码都能够通过测试：

    整数和浮点数：

    >>> assert lua.decode('3') == 3
    >>> assert lua.decode('4.1') == 4.1

    负浮点数：

    >>> assert lua.decode('-0.45') == -0.45

    科学计数法：

    >>> assert lua.decode('3e-7') == 3e-7
    >>> assert lua.decode('-3.23e+17') == -3.23e+17

    十六进制：

    >>> assert lua.decode('0x3a') == 0x3a

    字符串转义：

    >>> assert lua.decode(r"'test\'s string'") == "test's string"

    table：

    >>> data = '{ array = { 65, 23, 5 }, dict = { string = "value", array = { 3, 6, 4}, mixed = { 43, 54.3, false, string = "value", 9 } } }'
    >>> d = lua.decode(data)
    >>> # 下面是伪代码
    >>> d == lua.decode(lua.encode(d))

    table 中花括号之外的内容会被自动删除：

    >>> data = 'local data = {a = 1, b = {3, 4}} return data'
    >>> print(lua.decode(data))
    >>> {"a":1, {"b":[3,4]}}

    :param str text: lua字符串
    :return: python 对象
    :raise: :class:`TypeError`

    """
    return lua.decode(text)

def encode(obj):
    """将 python 对象解析成 lua 字符串。

    :param object obj: 一个 python 对象。
    :return: 一个 lua 格式的字符串。

    """
    return lua.encode(obj)

