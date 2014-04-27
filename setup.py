from setuptools import setup

setup(
    name="ArchMap",
    version="0.2",
    description="ArchMap geojson/kml generator",
    url="https://github.com/maelstrom59/ArchMap",
    license="Unlicense",
    py_modules=["archmap"],
    install_requires=["geojson", "simplekml"]
)
