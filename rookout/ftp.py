########################################
# ftp.py
# Author zrong(zengrong.net)
#
# Creation 2015-02-03
# Last Editing 2015-06-14
########################################

"""
.. module:: ftp
   :platform: Unix, Windows
   :synopsis: 封装 ftplib 的调用。

.. moduleauthor:: zrong(zengrong.net)

"""

import os
import ftplib
from rookout import slog

def get_ftp(ftp_conf, debug=0):
    """得到一个 已经打开的FTP 实例，和一个 ftp 路径。

    :param dict ftp_conf: ftp配置文件，格式如下：
    
        >>> {
        >>>     'server':'127.0.0.1',
        >>>     'start_path':None,
        >>>     'user':'admin',
        >>>     'password':'123456',
        >>> }

    :returns: ftp, ftpserverstr
    :rtype: :class:`ftplib.FTP` , str

    """
    server = ftp_conf.get('server')
    user = ftp_conf.get('user')
    password = ftp_conf.get('password')
    start_path = ftp_conf.get('start_path')
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

def upload_file(file_path, remote_path, ftp_conf, remove_file=False):
    """上传第一个指定的文件到 FTP 服务器。

    :param str file_path: 待上传文件的绝对路径。
    :param str remote_path: 文件在 FTP 服务器上的相对路径（相对于 FTP 服务器的初始路径）。
    :param dict ftp_conf: ftp配置文件，详见 :func:`get_ftp` 。
    :param bool remove_file: 上传成功后是否删除本地文件。
    :returns: FTP 服务器上的文件列表
    :rtype: list

    """
    check_ftp_conf(ftp_conf)

    ftp, ftpStr = get_ftp(ftp_conf)
    lf = open(file_path, 'rb')
    slog.info('Uploading "%s" to "%s/%s" ......'%(file_path, ftpStr, remote_path))
    ftp.storbinary("STOR %s"%remote_path, lf)
    filelist = ftp.nlst()
    ftp.quit()
    lf.close()
    if remove_file:
        os.remove(file_path)
    slog.info('Upload done.')
    return filelist

def download_file(remote_path, file_path, ftp_conf):
    check_ftp_conf(ftp_conf)
    ftp, ftpstr = get_ftp(ftp_conf)

    lf = open(file_path, 'wb')
    slog.info('Downloading "%s/%s" to "%s" ......'%(ftpstr, remote_path, lf.name))
    ftp.retrbinary('RETR %s'%remote_path, lf.write)
    ftp.quit()
    lf.close()
    slog.info('Download done.')
    return lf.name

def upload_dir(dir_name, upload_dir, ftp_conf):
    check_ftp_conf(ftp_conf)
    ftp, ftpStr = get_ftp(ftp_conf)
    if dir_name not in ftp.nlst():
        ftp.mkd(dir_name)
    ftp.cwd(dir_name)
    slog.info('Uploading "%s" to "%s/%s" ......'%(upload_dir, ftpStr, dir_name))
    rootLen = len(upload_dir) + 1

    for r,d,fl in os.walk(upload_dir):
        if r.split('/')[-1].startswith('.'):
            continue
        for sdir in d:
            if not sdir.startswith('.'):
                dirPath = r[rootLen:]
                if sdir not in ftp.nlst(dirPath):
                    dir_name = os.path.join(dirPath, sdir)
                    ftp.mkd(dir_name)
        for sf in fl:
            filePath = os.path.join(r, sf)
            f = open(filePath, 'rb')
            ftpPath = filePath[rootLen:]
            slog.info('%s -> %s', filePath, ftpPath)
            ftp.storbinary('STOR %s'%ftpPath, f)
            f.close()
    ftp.quit()

def check_ftp_conf(ftp_conf):
    if not ftp_conf \
    or not ftp_conf.get('server') \
    or not ftp_conf.get('user') \
    or not ftp_conf.get('password'):
        raise KeyError('ftp_conf MUST contains following values:'
                'server,user,password !')
