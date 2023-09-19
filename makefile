launch : build
	./Main/restart.py

build :
	python3 -m build
	pip install dist/golobot-0.0.1-py3-none-any.whl --force-reinstall

test : build
	'python3 -m unittest discover --start-directory Tests
