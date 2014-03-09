# Maintainer: Johannes Löthberg <johannes@kyriasis.com>

pkgname=archmap
pkgver=latest
pkgrel=1

pkgdesc="Generates a map of Arch Linux users"
arch=('any')
url="https://github.com/maelstrom59/ArchMap"
license=('custom:UNLICENSE')

depends=('python' 'python-geojson')
makedepends=('git')

install=archmap.install
source=('archmap::git+https://github.com/maelstrom59/ArchMap.git')
md5sums=('SKIP')

pkgver() {
	cd archmap
	git describe --tags | sed 's/^v//; s/-/-r/; s/-/./g'
}


package() {
	cd archmap
	install -D archmap.py "$pkgdir/usr/bin/archmap.py"

	install -d "$pkgdir/usr/lib/systemd/system"
	install -m644 systemd/archmap.{service,timer} "$pkgdir/usr/lib/systemd/system/"

	install -d "$pkgdir/usr/share/doc/archmap"
	install {README.md,archmap.conf,markers.kml} "$pkgdir/usr/share/doc/archmap"

	install -D -m644 UNLICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
