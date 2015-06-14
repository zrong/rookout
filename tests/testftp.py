import ftplib
from rookout.ftp import get_ftp

def test_get_ftp():
    ftpobj = get_ftp({
            'server':'127.0.0.1',
            'user':'user',
            'password':'password',
        })[0]
    print(ftpobj)
    assert isinstance(ftpobj, ftplib.FTP)
