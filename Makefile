
all: init test

init: 
	pip install -r requirements.txt

docs: clean-pyc
	$(MAKE) -C docs html

test:
	py.test tests

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
