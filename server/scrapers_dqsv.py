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

import datetime

from collections import namedtuple

from yaswfp import swfparser

Episode = namedtuple("Episode", "name occup bio image date")


class _ConstantPoolExtractor(object):
    """Get items from the constant pool."""
    def __init__(self, constants, actions):
        self.constants = constants
        self.actions = actions

    def get(self, *keys):
        """Get the text after some key."""
        values = {}
        stack = []
        for act in self.actions:
            if act.name == 'ActionPush':
                if act.Type == 7:
                    idx = act.Integer
                elif act.Type == 8:
                    idx = act.Constant8
                elif act.Type in (5, 6):
                    continue
                else:
                    raise ValueError("Bad act type: " + repr(act))
                try:
                    val = self.constants[idx]
                except IndexError:
                    stack.append(None)
                else:
                    if val.startswith('titulo') and val.endswith('1'):
                        # hard group break!!!
                        values = {}
                        stack = []
                    stack.append(val)
            elif act.name in ('ActionSetVariable', 'ActionSetMember'):
                if len(stack) == 2:
                    title, value = stack
                    if title in keys:
                        values[title] = value
                        if len(values) == len(keys):
                            return values
                stack = []
            else:
                stack = []


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
            if tag.CharacterID > 1:
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
    else:
        if len(images) < 3:
            # not enough images and no constant pool: a non-programs swf!
            return []

        raise ValueError("No ActionConstantPool found!")

    # do some magic to retrieve the texts
    items = []
    cpe = _ConstantPoolExtractor(act.ConstantPool, doaction.Actions)
    for i, image in enumerate(images, 1):
        name = 'titulo%d1' % i
        occup = 'titulo%d2' % i
        bio = 'htmlText'
        datestr = 'titulo%d3' % i
        vals = cpe.get(name, occup, bio, datestr)

        # get the date
        datestr = vals[datestr].split()[0]
        if "-" in datestr:
            datestr = "/".join(x.split("-")[0] for x in datestr.split("/"))
        dt = datetime.datetime.strptime(datestr, "%d/%m/%y")
        date = dt.date()

        ep = Episode(name=vals[name], occup=vals[occup],
                     bio=vals[bio], image=image, date=date)
        items.append(ep)
    return items
