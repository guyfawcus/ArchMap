#!/usr/bin/env python3
from setuptools import setup


# Find all of the tests in the 'tests' directory and return them.
def test_suite():
    import unittest
    suite = unittest.TestLoader().discover('tests')
    return suite


setup(
    name='archmap',
    version='0.5',
    description='ArchMap GeoJSON/KML generator',
    url='https://github.com/guyfawcus/ArchMap',
    license='Unlicense',
    py_modules=['archmap'],
    entry_points={'console_scripts': ['archmap=archmap:main']},
    install_requires=['bs4', 'geojson', 'simplekml'],
    test_suite='setup.test_suite',
    python_requires='>=3',
    include_package_data=True
)
