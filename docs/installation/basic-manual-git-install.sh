echo -e "==> Make and cd to ./ArchMap\n"
mkdir ArchMap && cd ArchMap

echo -e "\n\n==> Download the ArchMap repo from GitHub\n"
git clone https://github.com/guyfawcus/ArchMap.git ArchMap-git

echo -e "\n\n==> Install the required packages\n"
pip3 install -r ArchMap-git/requirements.txt

echo -e "\n\n==> Make an easy link to archmap.py\n"
cd ../ && ln -s ArchMap-git/archmap.py ./archmap

echo -e "\n\n==> Test by printing the help message\n"
./archmap --help
