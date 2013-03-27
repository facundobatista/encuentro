# FIXME: header and all that


import logging
import md5
import os

from twisted.web.client import getPage

from encuentro import platform

logger = logging.getLogger('encuentro.main')


class ImageGetter(object):
    """Image downloader and cache object."""

    def __init__(self, callback):
        self.callback = callback
        self.cache_dir = os.path.join(platform.cache_dir, 'encuentro.images')
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def get_image(self, episode_id, url):
        """Get an image and show it using the callback."""
        logger.info("Loading image for episode %s: %r", episode_id, url)
        file_name = md5.md5(url).hexdigest() + '.jpg'
        file_fullname = os.path.join(self.cache_dir, file_name)
        if os.path.exists(file_fullname):
            logger.debug("Image already available: %r", file_fullname)
            self.callback(episode_id, file_fullname)
            return

        def _d_callback(data, episode_id, file_fullname):
            """Cache the image and use the callback."""
            logger.debug("Image downloaded for episode_id %s, saving to %r",
                         episode_id, file_fullname)
            temp_file_name = file_fullname + '.tmp'
            with open(temp_file_name, 'wb') as fh:
                fh.write(data)
            os.rename(temp_file_name, file_fullname)
            self.callback(episode_id, file_fullname)

        logger.debug("Need to download the image")
        d = getPage(url)
        d.addCallback(_d_callback, episode_id, file_fullname)
        # FIXME: add an errback to log on error
