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

from yaswfp import swfparser


class _ConstantPoolExtractor(object):
    """Get items from the constant pool."""
    def __init__(self, items):
        self.items = items

    def get(self, key):
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


def scrap(fh):
    """Get useful info from a program."""
    swf = swfparser.SWFParser(fh)

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

    # do some magic to retrieve the values
    items = []
    cpe = _ConstantPoolExtractor(act.ConstantPool)
    for i in range(1, 5):
        name = cpe.get('titulo%d1' % (i,))
        title = cpe.get('titulo%d2' % (i,))
        descrip = cpe.get('entre%d' % (i,))
        items.append((name, title, descrip))
    return items
