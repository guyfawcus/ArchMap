Contribute
==========

.. contents:: In this section:
   :depth: 2
   :local:


Roadmap
-------

- Add more tests

- Work on packaging

- Use GitHub pages to build a homepage

  - Use `Leaflet <http://leafletjs.com/>`_ to get and display coords on a ...
  - `MapBox <https://www.mapbox.com/>`_ map


Contributing
------------

Contributions are always welcome! Here are a few ways you could contribute:

- Bug fixes
- New tests
- New features
- Testing on different platforms
- Documentation

Support: :ref:`external-links`


Development
-----------

All of the following commands assume you are are starting in the root ``ArchMap`` directory.

System Requirements
^^^^^^^^^^^^^^^^^^^

In addition to the :ref:`install-reqs` for the install, the following packages are required:

- To generate these docs:

  - sphinx

- For packaging:

  - setuptools
  - wheel (optional) - for building :ref:`wheels <build-wheel>`

Documentation
^^^^^^^^^^^^^

`Sphinx <http://sphinx-doc.org/>`_ can be used to build a variety of
`formats <http://sphinx-doc.org/invocation.html#invocation>`_.

First, make sure you're in the docs directory::

    cd docs/

Make the preferred output::

    make html

Open the the index page in your browser::

    firefox _build/html/index.html

Testing
^^^^^^^

``unittest`` is used for testing::

    python setup.py test

This will search the ``tests`` directory for tests.

See also:

* `unittest - Python docs <https://docs.python.org/3.4/library/unittest.html>`_

.. _packaging:

Packaging
^^^^^^^^^

ArchMap is currently packaged in two forms.

Arch Linux package
""""""""""""""""""
Packages are built using the ``PKGBUILD`` and ``archmap.install`` for settings.

To build package using the `PKGBUILD <https://wiki.archlinux.org/index.php/PKGBUILD>`_::

    cd pkgbuild
    makepkg PKGBUILD

Related issues:

* `#3 <https://github.com/maelstrom59/ArchMap/pull/3>`_ PKGBUILD - **Closed**
* `#9 <https://github.com/maelstrom59/ArchMap/pull/9>`_ PKGBUILD: Update pkgbuild with new deps and manpage - **Closed**

See also:

* `Creating packages <https://wiki.archlinux.org/index.php/Creating_packages>`_
* `Python Package Guidelines <https://wiki.archlinux.org/index.php/Python_Package_Guidelines>`_

Python package
""""""""""""""
Packages are built using ``setup.py`` and ``setup.cfg`` for settings.

To build a `source distribution <http://packaging.python.org/en/latest/glossary.html#term-source-distribution-or-sdist>`_::

   python setup.py sdist

.. _build-wheel:

To build a `wheel <http://packaging.python.org/en/latest/glossary.html#term-wheel>`_::

   python setup.py bdist_wheel

Related issues:

* `#8 <https://github.com/maelstrom59/ArchMap/issues/8>`_ Build a python package - **Open**

See also:

* `Installation & Packaging Tutorial <http://packaging.python.org/en/latest/tutorial.html>`_
