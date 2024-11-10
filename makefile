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
	cp secrets_template.py GBsecrets.py
	cd Main && ln -s ../GBsecrets.py . && cd ..
	echo "secrets.py à remplir manuellement"

pid :
	touch discord.pid

logs :
	touch logs/dev.log
	touch logs/error.log
	touch logs/dm.log

data :
	echo {} > Data/settings.json
	echo {} > Data/annonces_streams.json
	echo {} > Data/qpup.json

# À utiliser pour le premier démarrage du bot, crée tous les fichiers dans .gitignore
setup : secrets pid
	mkdir logs
	make logs
	mkdir Data
	make data

reset : clean_pip clean_settings build logs data
