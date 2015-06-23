For all
=======

Debian
------

- Update version number in the version file:

    echo VERSION > version.txt

- Check all is crispy

    ./setup.py clean build
    ./setup.py clean install --prefix=/tmp/test
    ./setup.py clean sdist

- Tag the release:

    bzr tag release_VERSION_WITH_UNDERSCORES

- Create a list of changes, and edit the changelog:

    - EDITOR=vim dch

    - put the list of changes

    - put proper version inside parenthesis

    - put 'unstable' in the OS version

- Build a tarball

    python setup.py sdist

- Build the .deb

    debuild -us -uc

- Move the tarball that we'll use, clean dir, adapt names

    mv dist/* ..
    cd ..
    mv encuentro_VERSION_all.deb encuentro-VERSION.deb
    (more cleaning: note that you'll find a heavy tarball and the one that you just moved)

- Sign both tarball and deb file

   gpg --armor --sign --detach-sig encuentro-VERSION.tar.gz
   gpg --armor --sign --detach-sig encuentro-VERSION.deb


Windows
-------

Proper instructions in windows/como_armar_la_parte_windows.txt (Spanish only).
