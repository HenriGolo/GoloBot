setup_venv :
	sudo apt install virtualenvwrapper
	source /usr/share/virtualenvwrapper/virtualenvwrapper.sh
	mkvirtualenv GoloBot-venv
	deactivate

build :
	./golobotvenv.sh 'python3 -m build'
	./golobotvenv.sh 'pip install dist/golobot-0.0.1-py3-none-any.whl --force-reinstall'

test : build
	./golobotvenv.sh 'python3 -m unittest discover --start-directory Tests'

launch : build
	./golobotvenv.sh ./Main/restart.py
