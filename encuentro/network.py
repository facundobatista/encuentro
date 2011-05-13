# -*- coding: utf8 -*-

# -*- coding: utf-8 -*-
#
# Copyright 2011 Facundo Batista
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# For further info, check  https://launchpad.net/encuentro

"""Some functions to deal with network and Encuentro site."""

import os
import re
import time
import uuid

from multiprocessing import Process, Event
from multiprocessing.queues import Queue
from Queue import Empty

from zope.testbrowser.browser import Browser
from mechanize._mechanize import LinkNotFoundError

from twisted.internet import defer, reactor
from twisted.web import client

URL = "http://descargas.encuentro.gov.ar/emision.php?emision_id=%d"
SERVER = "descargas.encuentro.gov.ar"

LINKSIZE = re.compile('.*?(\d+) MB\).*')

RE_SACATIT = re.compile('<h1 class="titFAQ">([^<]*)</h1>')
RE_SINOPSIS = re.compile('<p class="sinopsisTXT">([^<]*)</p>')
RE_TEMATICA = re.compile('<h2>Tem&aacute;tica:</h2>[^<]*<p>([^<]*)</p>')
RE_DURACION = re.compile('<h2>Duraci&oacute;n:</h2>[^<]*<p>([^<]*)</p>')

RE_DESCARGA = re.compile('Descargar ca.*completo.*')


CHUNK = 16 * 1024


class EpisodeData(object):
    """Episode data."""
    _liststore_order = {
        'titulo': 0,
        'seccion': 1,
        'tematica': 2,
        'duracion': 3,
        'nroemis': 4,
        'state': 5,        # note that state and progress both point to row 5,
        'progress': 5,     # because any change in these will update the row
    }
    def __init__(self, titulo, seccion, sinopsis, tematica, duracion, nroemis,
                 state=None, progress=None, filename=None):
        self.titulo = titulo
        self.seccion = seccion
        self.sinopsis = sinopsis
        self.tematica = tematica
        self.duracion = duracion
        self.state = Status.none if state is None else state
        self.progress = progress
        self.filename = filename
        self.nroemis = nroemis

    def get_row_data(self):
        """Return the data for the liststore row."""
        data = (self.titulo, self.seccion, self.tematica,
                self.duracion, self.nroemis, self._get_nice_state())
        return data

    def _get_nice_state(self):
        """A nicer state wording."""
        if self.state == Status.none:
            state = ''
        elif self.state == Status.waiting:
            state = 'Esperando'
        elif self.state == Status.downloading:
            state = 'Descargando: %s' % self.progress
        elif self.state == Status.downloaded:
            state = 'Terminado'
        else:
            raise ValueError("Bad state value: %r" % (self.state,))
        return state

    def update(self, row, **kwargs):
        """Update own attributes and value in the row."""
        for k, v in kwargs.items():
            setattr(self, k, v)
            try:
                pos = self._liststore_order[k]
            except KeyError:
                pass  # not a shown value
            else:
                if k == 'state' or k == 'progress':
                    v = self._get_nice_state()
                row[pos] = v


class Status(object):
    """Status constants."""
    none, waiting, downloading, downloaded = \
                                'none waiting downloading downloaded'.split()


class MiBrowser(Process):
    """Browser en otro proceso."""

    def __init__(self, authuser, authpass, url,
                 input_queue, output_queue, must_quit):
        self.authinfo = authuser, authpass
        self.url = url
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.must_quit = must_quit
        Process.__init__(self)

    def run(self):
        """Do the heavy work."""
        # set up
        browser = Browser()
        browser.mech_browser.set_handle_robots(False)

        # open the url and send the content
        browser.open(self.url)
        self.output_queue.put(browser.contents)

        # get the filename and download
        fname = self.input_queue.get()
        try:
            link = browser.getLink(text=RE_DESCARGA)
        except LinkNotFoundError:
#            print "    no estamos logueados, mandamos user y password"
            login = browser.getForm(index=1)
            usr = login.getControl(name='user')
            pss = login.getControl(name='pass')
            usr.value, pss.value = self.authinfo
            login.submit()

            # let's try to get the link again
            link = browser.getLink(text=RE_DESCARGA)

        m = LINKSIZE.match(link.text)
        if m:
            filesize = m.groups()[0]
#            print "    tamaño aprox (MB):", filesize
        else:
            filesize = "?"
            print "WARNING: Texto del link raro:", repr(link.text)
        link.click()

        response = browser.mech_browser.response()
        aout = open(fname, "w")
        tot = 0
        while not self.must_quit.is_set():
            r = response.read(CHUNK)
            if r == "":
                break
            aout.write(r)
            tot += CHUNK / (1024.0 ** 2)
            m = "%.1f de %s MB" % (tot, filesize)
            self.output_queue.put(m)
        self.output_queue.put('done')


class DeferredQueue(Queue):
    """A Queue with a deferred get."""

    _reactor_period = .5

    def deferred_get(self):
        """Return a deferred that is triggered when data."""
        d = defer.Deferred()

        def check():
            try:
                data = self.get(block=False)
            except Empty:
                # no data, check again later
                reactor.callLater(self._reactor_period, check)
            else:
                # have some data, let's check if there's more
                all_data = [data]
                try:
                    while True:
                        all_data.append(self.get(block=False))
                except Empty:
                    # we're done!
                    d.callback(all_data)

        reactor.callLater(self._reactor_period, check)
        return d


class Downloader(object):
    """Episode downloader."""
    def __init__(self, config):
        self.config = config
        self._prev_progress = None
        self.browser_quit = set()

    def shutdown(self):
        """Quit the download."""
        for bquit in self.browser_quit:
            bquit.set()

    @defer.inlineCallbacks
    def download(self, nroemis, cb_progress):
        """Descarga una emisión a disco."""
        # levantamos el browser
        qinput = DeferredQueue()
        qoutput = Queue()
        url = URL % nroemis
        bquit = Event()
        self.browser_quit.add(bquit)
        authuser = self.config.get('user', '')
        authpass = self.config.get('password', '')
        brow = MiBrowser(authuser, authpass, url, qoutput, qinput, bquit)
        brow.start()

        # esperamos hasta que la pag esté
        pag = (yield qinput.deferred_get())[0]

        # obtenemos sección y titulo
        m = RE_SACATIT.search(pag)
        if m:
            alltit = m.group(1).decode('utf8').strip()
            if alltit == u'-':
                print "WARNING: quiso bajar %d pero no existe" % (nroemis,)
                return
            titulo, seccion = alltit.rsplit(" - ", 1)
        else:
            print "WARNING: No pude obtener el título/sección"
            titulo = str(uuid.uuid4())
            seccion = "Desconocido"
        downloaddir = self.config.get('downloaddir', '')
        fname = os.path.join(downloaddir, seccion, titulo + u".avi")

        # ver si esa seccion existe, sino crearla
        dirsecc = os.path.dirname(fname)
        if not os.path.exists(dirsecc):
            os.makedirs(dirsecc)

        # descargamos en un temporal
        tempf = fname + str(time.time())
        qoutput.put(tempf)

        # loop reading until finished
        self._prev_progress = None

        while True:
            # get all data and just use the last item
            data = (yield qinput.deferred_get())[-1]
            if data == 'done':
                break

            # actualizamos si hay algo nuevo
            if data != self._prev_progress:
                cb_progress(data)
                self._prev_progress = data

        # movemos al nombre correcto y terminamos
        os.rename(tempf, fname)
        self.browser_quit.remove(bquit)
        defer.returnValue(fname)


def _parsea_datos_emision(pag, nroemis):
    """Saca los datos de emisión del html."""

    m = RE_SACATIT.search(pag)
    if m:
        alltit = m.group(1).decode('utf8').strip()
        if alltit == u'-':
            # esta emisión no existe!
            return
        titulo, seccion = alltit.rsplit(" - ", 1)
    else:
        print "Warning: No pude obtener el título/sección"
        titulo = None
        seccion = None

    m = RE_SINOPSIS.search(pag)
    if m:
        sinopsis = m.group(1).decode('utf8').strip()
    else:
        print "Warning: No pude obtener la sinopsis"
        sinopsis = None

    m = RE_TEMATICA.search(pag)
    if m:
        tematica = m.group(1).decode('utf8').strip()
    else:
        print "Warning: No pude obtener la temática"
        tematica = None

    m = RE_DURACION.search(pag)
    if m:
        strdur = m.group(1)
        if ':' in strdur:
            h, m, s = map(int, strdur.split(':'))
            duracion = h * 60 + m      # discard seconds
        else:
            duracion = int(strdur)
    else:
        print "Warning: No pude obtener la duracion"
        duracion = None

    de = EpisodeData(titulo=titulo, seccion=seccion, sinopsis=sinopsis,
                     tematica=tematica, duracion=duracion, nroemis=nroemis)
    return de


@defer.inlineCallbacks
def get_datos_emision(nroemis):
    """Trae los datos de una emisión."""
    pag = yield client.getPage(URL % nroemis)
    defer.returnValue(_parsea_datos_emision(pag, nroemis))


if __name__ == "__main__":
    # test datos emision
    parte_html_real = """

<div id="contenidos">
<div id="multimedia">
<p id="titMediateca">Videos &amp; Descargas</p>
	
<div id="tituloEmision"><h1 class="titFAQ">Chacra orgánica - Entornos invisibles</h1><ul><li class="stIcons"><a id="ck_email" class="stbar chicklet" href="javascript:void(0);">E-mail</a></li>
<li class="stIcons"><a id="ck_facebook" class="stbar chicklet" href="javascript:void(0);">Facebook</a></li>
<li class="stIcons"><a id="ck_twitter" class="stbar chicklet" href="javascript:void(0);">Twitter</a></li>
     <li class="stIcons"><a id="ck_sharethis" class="stbar chicklet" href="javascript:void(0);">Compartir</a></li>
	</ul>
        <script type="text/javascript">
	var shared_object = SHARETHIS.addEntry({
	title: document.title,
	url: document.location.href
});

>
shared_object.attachButton(document.getElementById("ck_sharethis"));
shared_object.attachChicklet("email", document.getElementById("ck_email"));
shared_object.attachChicklet("facebook", document.getElementById("ck_facebook"));
shared_object.attachChicklet("twitter", document.getElementById("ck_twitter"));

</script></div><div class="metadataVideo"><div class="datosVideo"><p class="diaHorario"></p>
<h2 class="sinopsis">Sinopsis:</h2>
<p class="sinopsisTXT">Las ranas se burlaban del quirquincho, porque quería ser músico. Hasta que un día…
</p>

<h2>Tem&aacute;tica:</h2>
<p>Infantiles</p>
<h2>Duraci&oacute;n:</h2>
<p>5</p>
<h2>Etiquetas:</h2>

<p> <a href="http://descargas.encuentro.gov.ar/tags.php?tag_id=11">Pakapaka</a>  <a href="http://descargas.encuentro.gov.ar/tags.php?tag_id=98">cuentos</a>  <a href="http://descargas.encuentro.gov.ar/tags.php?tag_id=42">pueblos originarios</a>  <a href="http://descargas.encuentro.gov.ar/tags.php?tag_id=54">animación</a> </p>
</div><ul class="botonesFichaIdeas"><li><a href="" class="ficha">Ficha del programa</a></li></ul></div><h2 class="titFAQ">Mir&aacute; el cap&iacute;tulo on line</h2>
<div class="videoCapitulo"><!--[if !IE]> -->

   <object type="application/x-shockwave-flash" data="flvplayer.swf" width="360" height="288">
    <!-- <![endif]-->
"""

#    de = _parsea_datos_emision(parte_html_real)
#    assert de.titulo == u"Chacra orgánica"
#    assert de.seccion == u"Entornos invisibles"
#    assert de.sinopsis == u'Las ranas se burlaban del quirquincho, porque quería ser músico. Hasta que un día…'
#    assert de.tematica == u'Infantiles'
#    assert de.duracion == 5
#
#
#    # bajamos una pag
#    def show(r):
#        print "Descargado?:", repr(r)
#        reactor.stop()
#    d = get_datos_emision(1)
#    d.addCallback(show)

    def show(avance):
        print "Avance:", avance
    downloader = Downloader('.', "pass", "clave")
    downloader.download(107, show)




    reactor.run()


