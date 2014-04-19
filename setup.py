from setuptools import setup

setup(
    name="ArchMap",
    version="0.2",
    description="ArchMap geojson/kml generator",
    url="https://github.com/maelstrom59/ArchMap",
    licence="Unlicense",
    packages="archmap.py",
    install_requires=["geojson", "simplekml", "github3.py"]
)
