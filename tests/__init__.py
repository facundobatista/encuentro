# let's make sure we don't access the network in the tests

try:
    import urllib2
    mod = urllib2
except ImportError:
    from urllib import request
    mod = request


def _f(*a, **k):
    raise ValueError("You are trying to hit the network!")

mod.urlopen = _f
