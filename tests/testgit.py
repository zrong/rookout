from zrong import git

def setup():
    pass

def test_getArgs():
    assert len(git.getArgs('')) == 1
    assert len(git.getArgs(None, 'a', 'b')) == 3

def test_getHash():
    assert len(git.getHash('')) == 40
    assert len(git.getHash('', 7)) == 7

def test_getCommitTimes():
    assert git.getCommitTimes('') > 0
