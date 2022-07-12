from rattle.utils.weakkeydefaultdict import WeakKeyDefaultDictionary

import inspect


def test_construct():
    """assert that creating a weak dictionary goes without an error"""
    WeakKeyDefaultDictionary(lambda _: None)


def test_missing_key():
    wk = WeakKeyDefaultDictionary(lambda k: k)
    k = inspect.currentframe()
    assert wk[k] is k
