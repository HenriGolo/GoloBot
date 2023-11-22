update : pull build start

start :
	Main/restart.py

pull :
	git pull

build :
	python3 -m build
	pip install dist/golobot-0.0.1-py3-none-any.whl --force-reinstall

test : build
	python3 -m unittest discover --start-directory Tests
