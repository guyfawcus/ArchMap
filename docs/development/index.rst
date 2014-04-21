Contribute
==========

.. contents:: In this section:
   :depth: 1
   :local:


Roadmap
-------

- Work on packaging

- Use GitHub pages to build a homepage

  - Use `Leaflet <http://leafletjs.com/>`_ to get and display coords on a ...
  - `MapBox <https://www.mapbox.com/>`_ map


Contributing
------------

Contributions are always welcome! Here are a few ways you could contribute:

- Bug fixes
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
  - wheel

Documentation
^^^^^^^^^^^^^

.. code-block:: bash

   cd docs/
   make html

Packaging
^^^^^^^^^

`kyrias <https://github.com/kyrias>`_ has worked on the
`Arch Linux packaging <https://github.com/maelstrom59/ArchMap/tree/master/pkgbuild>`_.

Python packaging is currently in the works, have a look at this
`issue <https://github.com/maelstrom59/ArchMap/issues/8>`_
if you can help in any way.

.. code-block:: bash

   python setup.py bdist_wheel
