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

clean :
	pip freeze > piplist.txt
	pip uninstall -r piplist.txt -y
	rm piplist.txt
	pip install build
	echo {} > logs/settins.json

reset : clean build
