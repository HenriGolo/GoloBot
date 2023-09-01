build :
	./my_virtualenv.sh 'python3 -m build'
	./my_virtualenv.sh 'pip install dist/golobot-0.0.1-py3-none-any.whl --force-reinstall'

test : build
	./my_virtualenv.sh 'python3 -m unittest discover --start-directory Tests'

launch : build
	./my_virtualenv.sh 'python3 restart.py'
