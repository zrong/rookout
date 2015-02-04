"""zrong 编写的基于 python 3.4 的通用功能封装。

.. moduleauthor:: zrong(zengrong.net)

"""

import logging

__version__ = "0.1.5"
__all__ = ['base', 'git', 'lua', 'ftp']

slog = logging.getLogger("system")
"""默认的系统 log。"""

__LOG_FMT = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s\n")

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
