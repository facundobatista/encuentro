#!/usr/bin/env python3

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
import sys

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


def _fix_date(date):
    """Fix and improve the date info."""
    datestr = date.split()[0]
    if datestr.isupper():
        return None

    if "-" in datestr:
        datestr = "/".join(x.split("-")[0] for x in datestr.split("/"))
    dt = datetime.datetime.strptime(datestr, "%d/%m/%y")
    date = dt.date()
    return date


def _fix_occup(occup):
    """Fix and improve the occupation info."""
    occup = occup.strip()
    if not occup:
        return ""
    occup = occup[0].upper() + occup[1:]
    if occup[-1] != ".":
        occup = occup + "."

    # assure all the letters after a period is in uppercase
    pos_from = 0
    while True:
        try:
            pos = occup.index(".", pos_from)
        except ValueError:
            break
        pos_from = pos + 1
        pos += 2   # second letter after the point
        if pos < len(occup):
            occup = occup[:pos] + occup[pos].upper() + occup[pos + 1:]

    return occup


def _fix_bio(bio):
    """Fix and improve the bio info."""
    bio = bio.strip()
    return bio


def _fix_name(name):
    """Fix and improve the name info."""
    name = name.replace("&quot;", '"')
    return name


def scrap(fh, custom_order=None):
    """Get useful info from a program."""
    swf = swfparser.SWFParser(fh)

    # get the images
    base = None
    images = []
    for tag in swf.tags:
        if tag.name == 'JPEGTables':
            base = tag.JPEGData
        elif tag.name == 'DefineBits':
            images.append((tag.CharacterID, tag.JPEGData))
        elif tag.name == 'DefineBitsJPEG2':
            images.append((tag.CharacterID, tag.ImageData))
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
    cpe = _ConstantPoolExtractor(act.ConstantPool, doaction.Actions)
    i = 0
    all_vals = []
    while True:
        i += 1
        name = 'titulo%d1' % i
        occup = 'titulo%d2' % i
        bio = 'htmlText'
        date = 'titulo%d3' % i
        vals = cpe.get(name, occup, bio, date)
        if vals is None:
            break
        all_vals.append((vals[name], vals[occup], vals[bio], vals[date]))

    items = []
    for i, (name, occup, bio, date) in enumerate(all_vals):
        date = _fix_date(date)
        if date is None:
            continue
        occup = _fix_occup(occup)
        bio = _fix_bio(bio)
        name = _fix_name(name)

        # use the corresponding image, or through the custom order
        if custom_order is None:
            idx = i
        else:
            idx = custom_order.index(name)
        image = images[idx]

        ep = Episode(name=name, occup=occup, bio=bio, image=image, date=date)
        items.append(ep)
    return items


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: scrapers_dqsv.py file.swf")
        exit()

    custom_order = None
    #custom_order = [
    #    u"",
    #]

    with open(sys.argv[1], 'rb') as fh:
        episodes = scrap(fh, custom_order)
    for i, ep in enumerate(episodes):
        print("Saving img {} for {}".format(i, ep.name))
        with open("scraper-img-{}.jpeg".format(i), "wb") as fh:
            fh.write(ep.image)
