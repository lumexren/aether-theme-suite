.PHONY: check sync artwork package-vscode install dry-run uninstall

check:
	python3 scripts/sync-palette.py --check
	bash -n install.sh scripts/package-vscode.sh

sync:
	python3 scripts/sync-palette.py --write

artwork:
	python3 scripts/render-artwork.py

package-vscode:
	./scripts/package-vscode.sh

install:
	./install.sh

dry-run:
	./install.sh --dry-run

uninstall:
	./install.sh --uninstall
