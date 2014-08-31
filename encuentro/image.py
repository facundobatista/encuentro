# Copyright 2013-2014 Facundo Batista
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

"""Get an image from web and cache it."""


import logging
import md5
import os
import glob

from encuentro import multiplatform, utils

logger = logging.getLogger('encuentro.image')


class ImageGetter(object):
    """Image downloader and cache object."""

    def __init__(self, callback):
        self.callback = callback
        self.cache_dir = os.path.join(multiplatform.cache_dir,
                                      'encuentro.images')
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def get_image(self, episode_id, url):
        """Get an image and show it using the callback."""
        logger.info("Loading image for episode %s: %r", episode_id, url)
        file_name = md5.md5(url).hexdigest()
        file_fullname = os.path.join(self.cache_dir, file_name)
        img_search_result = glob.glob(file_fullname + '.*')
        if len(img_search_result) > 0:
            logger.debug("Image already available: %r", file_fullname)
            self.callback(episode_id, file_fullname)
            return

        def _d_callback(data, episode_id, file_fullname):
            """Cache the image and use the callback."""
            content_type, img_data = data
            content, extension = content_type.split('/')
            if content != 'image':
                logger.debug("The Content-Type header is not 'image'")
            file_fullname = file_fullname + '.' + extension
            logger.debug("Image downloaded for episode_id %s, "
                         "saving to %r, Content-Type= %s",
                         episode_id, file_fullname, content_type)
            with utils.SafeSaver(file_fullname) as fh:
                fh.write(img_data)
            self.callback(episode_id, file_fullname)

        def _d_errback(failure):
            """Log the problem."""
            logger.error("Problem getting image: type: %s error: %s",
                         failure.type, failure.value)

        logger.debug("Need to download the image")
        d = utils.download(url)
        d.add_callback(_d_callback, episode_id, file_fullname)
        d.add_errback(_d_errback)
