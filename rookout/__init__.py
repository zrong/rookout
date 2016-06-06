# coding: utf-8
#########################################
# __init__.py
#
# Author zrong(zengrong.net)
# Creation 2014-09-23
# Last Editing 2015-06-14
#########################################
"""zrong 编写的基于 python 3.4 的通用功能封装。

.. moduleauthor:: zrong(zengrong.net)

"""

import logging
import sys

__version__ = "0.5.1"
__all__ = ['base', 'git', 'lua', 'ftp', 'gettext', 'conf']

slog = logging.getLogger("system")
"""默认的系统 log。"""

__LOG_FMT = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s\n")


# 可改为使用：https://github.com/limodou/uliweb/blob/master/uliweb/utils/coloredlog.py
# 和 https://github.com/tartley/colorama
class ConsoleColor():
	RESET = "\033[0m"
	BOLD = "\033[1m"
	UNDERLINE = "\033[4m"
	BLINK = "\033[5m"
	REVERSE = "\033[7m"
	FADE = "\033[8m"

	BLACK = "\033[30m"
	RED = "\033[31m"
	GREEN = "\033[32m"
	YELLOW = "\033[33m"
	BLUE = "\033[34m"
	MAGENTA = "\033[35m"
	CYAN = "\033[36m"
	WHITE = "\033[37m"

	BG_BLACK = "\033[40m"
	BG_RED = "\033[41m"
	BG_GREEN = "\033[42m"
	BG_YELLOW = "\033[43m"
	BG_BLUE = "\033[44m"
	BG_MAGENTA = "\033[45m"
	BG_CYAN = "\033[46m"
	BG_WHITE = "\033[47m"

        # 黑底彩色
	# B2_BLACK = "\033[90m"
	# B2_RED = "\033[91m"
	# B2_GREEN = "\033[92m"
	# B2_YELLOW = "\033[93m"
	# B2_BLUE = "\033[94m"
	# B2_MAGENTA = "\033[95m"
	# B2_CYAN = "\033[96m"
	# B2_WHITE = "\033[97m"


class ColoredStreamHandler(logging.StreamHandler):
    def format(self, record):
        msg = super(ColoredStreamHandler, self).format(record)
        if sys.platform == 'win32':
            return msg
        if record.levelno >= logging.ERROR:
            msg = ConsoleColor.RED+msg+ConsoleColor.RESET
        elif record.levelno == logging.WARNING:
            msg = ConsoleColor.YELLOW+msg+ConsoleColor.RESET
        return msg

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
