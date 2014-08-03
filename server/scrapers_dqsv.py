# -*- coding: utf-8 -*-

# Copyright 2014 Facundo Batista
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

"""Scrapers for the decimequiensosvos backend."""

from collections import namedtuple

from yaswfp import swfparser

Episode = namedtuple("Episode", "name occup bio image")


class _ConstantPoolExtractor(object):
    """Get items from the constant pool."""
    def __init__(self, items, keys):
        self.items = items
        self.keys = keys

    def _get(self, key):
        """Get the text after some key."""
        texts = iter(self.items)
        for t in texts:
            if t == key:
                break

        value = next(texts)
        if value == 'dataEntre':
            # it's the main one, go after the htmlText key
            for t in texts:
                if t == 'htmlText':
                    break
            value = next(texts)

        return value

    def __iter__(self):
        pos = 1
        while True:
            vals = [self._get(key % pos) for key in self.keys]
            yield vals
            pos += 1


def scrap(fh):
    """Get useful info from a program."""
    swf = swfparser.SWFParser(fh)

    # get the images
    base = None
    images = []
    for tag in swf.tags:
        if tag.name == 'JPEGTables':
            base = tag.JPEGData
        if tag.name == 'DefineBits':
            images.append((tag.CharacterID, tag.JPEGData))
    images = [base + x[1] for x in sorted(images, reverse=True)]

    # get the last DefineSprite
    defsprite = None
    for tag in swf.tags:
        if tag.name == 'DefineSprite':
            defsprite = tag
    assert tag is not None, "DefineSprite not found"

    # get the actions
    doaction = defsprite.ControlTags[0]
    for act in doaction.Actions:
        if act.name == 'ActionConstantPool':
            break

    # do some magic to retrieve the texts
    items = []
    keys = ['titulo%d1', 'titulo%d2', 'entre%d']
    cpe = _ConstantPoolExtractor(act.ConstantPool, keys)
    for (name, occup, descrip), image in zip(cpe, images):
        items.append(Episode(name=name, occup=occup, bio=descrip, image=image))
    return items
