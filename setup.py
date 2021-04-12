#!/usr/bin/env python3

# Copyright 2011-2021 Facundo Batista
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

"""Build tar.gz for encuentro."""

from setuptools import setup


LONG_DESCRIPTION = (
    'Simple application that allows to search, download '
    'and see the content of the Encuentro channel.'
)

with open("requirements.txt", "rt", encoding='utf8') as fh:
    requirements = fh.read().split('\n')

setup(
    name='encuentro',
    version=open('encuentro/version.txt').read().strip(),
    license='GPL-3',
    author='Facundo Batista',
    author_email='facundo@taniquetil.com.ar',
    description='Search, download and see the wonderful Encuentro content.',
    long_description=LONG_DESCRIPTION,
    url='https://launchpad.net/encuentro',

    packages=[
        "encuentro",
        "encuentro.ui",
    ],
    package_data={
        "encuentro": ["ui/media/*", "logos/icon-*.png", "version.txt"],
    },
    entry_points={
        'console_scripts': ["encuentro = encuentro.main:main"],
    },
    install_requires=requirements,
)
