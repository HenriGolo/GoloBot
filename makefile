.NOTPARALLEL: update

update : pull build start

start :
	Main/restart.sh

pull :
	git pull

build :
	python3 -m build
	pip install dist/golobot-0.0.1-py3-none-any.whl --force-reinstall

test : build
	python3 -m unittest discover --start-directory Tests

clean_pip :
	pip freeze > piplist.txt
	pip uninstall -r piplist.txt -y
	rm piplist.txt
	pip install build


secrets :
	cp .env.example .env
	echo ".env à remplir manuellement"

logs :
	touch logs/dev.log
	touch logs/error.log
	touch logs/dm.log

data :
	echo {} > Data/settings.json
	echo {} > Data/annonces_streams.json
	echo {} > Data/qpup.json

# À utiliser pour le premier démarrage du bot, crée tous les fichiers dans .gitignore
setup : secrets
	mkdir -p logs
	make logs
	mkdir -p Data
	make data

check_env_path:
	@for f in .env .env.*; do \
		[ -f "$$f" ] || continue; \
		if ! grep -q '^PATH=' "$$f"; then \
			tmpfile=$$(mktemp); \
			echo "PATH=$$(pwd)" > "$$tmpfile"; \
			cat "$$f" >> "$$tmpfile"; \
			mv "$$tmpfile" "$$f"; \
		fi \
	done

reset : clean_pip clean_settings build logs data
