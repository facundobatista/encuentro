# -*- coding: utf-8 -*-

# Copyright 2014-2015 Facundo Batista
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

from __future__ import unicode_literals

"""Tests for the helper of scrapers."""

import unittest

from server import helpers


class CleanHTMLTestCase(unittest.TestCase):
    """Test for the HTML cleaning function."""

    def test_remove_tags(self):
        t = "foo bar. \n<br><em>Baz Bardo</em> fruta."
        r = helpers.clean_html(t)
        self.assertEqual(r, "foo bar. \nBaz Bardo fruta.")

    def test_in_the_end_1(self):
        t = "Provincia de Salta.&nbsp;                      </p>"
        r = helpers.clean_html(t)
        self.assertEqual(r, "Provincia de Salta.")

    def test_in_the_end_2(self):
        t = "evento deportivo.&nbsp;"
        r = helpers.clean_html(t)
        self.assertEqual(r, "evento deportivo.")

    def test_tag_complex(self):
        t = '<span style="line-height: 1.22;">Alumnos y docente'
        r = helpers.clean_html(t)
        self.assertEqual(r, "Alumnos y docente")
