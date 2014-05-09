echo -e "==> Make and cd to ./ArchMap\n"
mkdir ArchMap && cd ArchMap

echo -e "\n\n==> Download the ArchMap repo from GitHub\n"
git clone https://github.com/maelstrom59/ArchMap.git ArchMap-git

echo -e "\n\n==> Download the geojsonio.py repo from GitHub so you can use --geojsonio\n"
git clone https://github.com/jwass/geojsonio.py.git geojsonio.py-git

echo -e "\n\n==> Convert geojsonio.py to python3\n"
2to3 -w geojsonio.py-git/geojsonio/geojsonio.py

echo -e "\n\n==> Install the required packages\n"
pip3 install -r ArchMap-git/requirements.txt

echo -e "\n\n==> Link the geojsonio module into the ArchMap-git directory\n"
cd ArchMap-git && ln -s ../geojsonio.py-git/geojsonio/geojsonio.py

echo -e "\n\n==> Make an easy link to archmap.py\n"
cd ../ && ln -s ArchMap-git/archmap.py ./archmap

echo -e "\n\n==> Test by printing the help message\n"
./archmap --help
