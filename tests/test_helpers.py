# Copyright 2014-2017 Facundo Batista
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


class EnhanceNumberTestCase(unittest.TestCase):
    """Tests for the enhancement of numbers."""

    def _check(self, src, dest):
        """Do the checking."""
        result = helpers.enhance_number(src)
        self.assertEqual(result, dest)

    def test_cap_only_simple(self):
        self._check("Cap.07", "Capítulo 07")

    def test_cap_only_spaced(self):
        self._check("Cap. 07", "Capítulo 07")

    def test_cap_title_simple(self):
        self._check("Cap.07 Foo Bar", "07. Foo Bar")

    def test_cap_title_single_digit(self):
        self._check("Cap.2 Foo Bar", "02. Foo Bar")

    def test_cap_title_spaced(self):
        self._check("Cap. 2 Foo Bar", "02. Foo Bar")

    def test_dashed_nothing(self):
        self._check("foo bar", "foo bar")

    def test_dashed_simple(self):
        self._check("1- foo bar", "01. foo bar")

    def test_dashed_no_number(self):
        self._check("foo - bar", "foo - bar")

    def test_dashed_twodigits(self):
        self._check("05 - foo bar", "05. foo bar")


class FakeIDGeneratorTestCase(unittest.TestCase):
    """Tests for the fake id generator."""

    def test_same(self):
        r = helpers.get_unique_id("foobar", {})
        self.assertEqual(r, "foobar")

    def test_simple(self):
        r = helpers.get_unique_id("foobar", {'foo', 'foobar', 'bar'})
        self.assertEqual(r, "foobar--1")

    def test_already_there_one(self):
        r = helpers.get_unique_id("foobar", {'foobar', 'foobar--1'})
        self.assertEqual(r, "foobar--2")

    def test_already_there_several(self):
        r = helpers.get_unique_id("foobar", {'foobar', 'foobar--1', 'foobar--2', 'foobar--3'})
        self.assertEqual(r, "foobar--4")

    def test_already_fake_simple(self):
        r = helpers.get_unique_id("foobar--1", {'foo', 'bar'})
        self.assertEqual(r, "foobar--1")

    def test_already_fake_already_there(self):
        r = helpers.get_unique_id("foobar--1", {'foobar--1', 'foobar--2'})
        self.assertEqual(r, "foobar--3")

    def test_already_fake_decen(self):
        r = helpers.get_unique_id("foobar--9", {'foobar--9'})
        self.assertEqual(r, "foobar--10")
