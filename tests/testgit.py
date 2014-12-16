from zrong import git

def setup():
    pass

def test_get_args():
    assert len(git.get_args('')) == 1
    assert len(git.get_args(None, 'a', 'b')) == 3

def test_get_hash():
    assert len(git.get_hash('')) == 40
    assert len(git.get_hash('', 7)) == 7

def test_get_commit_times():
    assert git.get_commit_times('') > 0

def test_isclean():
    git.isclean(None)

def test_get_branches():
    assert git.get_branches(None)

def test_call():
    code, output = git.call(None, '--aabbccdd')
    assert output
