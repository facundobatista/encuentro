from __future__ import with_statement

import codecs
import os
import re
import simplejson
import sys
import time
import urllib2


THEME_URL = "http://descargas.encuentro.gov.ar/jsonProgramasPorTema.php"
EPISODE_URL = "http://descargas.encuentro.gov.ar/emision.php?emision_id=%s"

RE_SACATIT = re.compile('<h1 class="titFAQ">([^<]*)</h1>')
RE_SINOPSIS = re.compile('<p class="sinopsisTXT">([^<]*)</p>')
RE_TEMATICA = re.compile('<h2>Tem&aacute;tica:</h2>[^<]*<p>([^<]*)</p>')
RE_DURACION = re.compile('<h2>Duraci&oacute;n:</h2>[^<]*<p>([^<]*)</p>')


def retryable(func):
    """Decorator to retry functions."""
    def _f(*args, **kwargs):
        for attempt in range(5, -1, -1):  # if reaches 0: no more attempts
            try:
                res = func(*args, **kwargs)
            except Exception, e:
                if not attempt:
                    raise
                print "   problem (retrying...):", e
                time.sleep(5)
            else:
                return res
    return _f


@retryable
def get_episodes_by_theme(tema):
    """Get all the episodes number of a theme."""
    req = urllib2.Request(THEME_URL, "tema_id=%d" % tema)
    print "Downloading theme", tema
    u = urllib2.urlopen(req)
    content = u.read()
    resp = simplejson.loads(content)
    eps = [x['emision_id'] for x in resp]
    print "   ok:", len(eps)
    return eps


def _episode_parser(pag):
    """Get the episode info out of the HTML."""

    m = RE_SACATIT.search(pag)
    if m:
        alltit = m.group(1).decode('utf8').strip()
        if alltit == u'-':
            # it doesn't really exist!
            return
        titulo, seccion = alltit.rsplit(" - ", 1)
    else:
        print "  Warning: couldn't get title/section"
        titulo = None
        seccion = None

    m = RE_SINOPSIS.search(pag)
    if m:
        sinopsis = m.group(1).decode('utf8').strip()
    else:
        print "  Warning: couldn't get sinopsis"
        sinopsis = None

    m = RE_TEMATICA.search(pag)
    if m:
        tematica = m.group(1).decode('utf8').strip()
    else:
        print "  Warning: couldn't get theme"
        tematica = None

    m = RE_DURACION.search(pag)
    if m:
        strdur = m.group(1)    # possibilities found: '26', '0:26:00', '0:2600'
        seps = strdur.count(':')
        if seps == 0:
            duracion = int(strdur)
        elif seps == 1:
            h, ms = strdur.split(':')
            h = int(h)
            assert len(ms) == 4, "Bad duration format: %r" % (strdur,)
            m = int(ms[:2])
            duracion = h * 60 + m
        elif seps == 2:
            h, m, s = map(int, strdur.split(':'))
            duracion = h * 60 + m
        else:
            raise ValueError("Bad duration format: %r" % (strdur,))
    else:
        print "  Warning: couldn't get duration"
        duracion = None

    d = dict(titulo=titulo, seccion=seccion, sinopsis=sinopsis,
             tematica=tematica, duracion=duracion)
    return d


@retryable
def get_episode_info(epis):
    """Get the info of the episode."""
    print "Downloading episode", epis
    u = urllib2.urlopen(EPISODE_URL % epis)
    pag = u.read()
    d = _episode_parser(pag)
    if d is not None:
        d['nroemis'] = epis
    return d


def main():
    themepis = {}
    for i in xrange(0, 50):
        eps = get_episodes_by_theme(i)
        if eps is None:
            print "Abort!"
            sys.exit()

        for ep in eps:
            themepis[int(ep)] = i

    allepis = sorted(themepis)
    print "Quantity of episodes:", len(allepis)

    all_data = []
    for epis in allepis:
        d = get_episode_info(epis)
        if d is None:
            print "WARNING: Episode %d does not exist! (from theme %d)" % (
                                                        epis, themepis[epis])
        else:
            all_data.append(d)

    info = simplejson.dumps(all_data)
    with codecs.open("encuentro-v01.json.tmp", "w", "utf8") as fh:
        fh.write(info)
    os.rename("encuentro-v01.json.tmp", "encuentro-v01.json")


if len(sys.argv) == 2:
    print get_episode_info(int(sys.argv[1]))
else:
    main()
