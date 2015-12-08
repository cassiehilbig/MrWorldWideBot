#
# Run
#

debug: install_test_dependencies
	dev_appserver.py --host 0.0.0.0 --port 8080 --admin_port 8000 --log_level=debug app.yaml

#
# Backend Tests
#

lint: install_test_dependencies
	flake8 .

# these are checked in, so only run this if you are adding new stuff.
install_backend_dependencies:
	pip install --upgrade --no-deps --requirement requirements_xlib.txt -t xlib
	rm -rf xlib/*.egg-info xlib/*.dist-info xlib/VERSION

install_test_dependencies:
	pip install --upgrade --quiet --requirement requirements.txt

test: lint
	python -m multitest discover -v -t . -s test

coverage: install_test_dependencies
	coverage run -m multitest discover -t . -s test 2> /dev/null
	coverage combine
	coverage report -m

.PHONY: debug test secrets deploy_application deploy deploy_staging \
	lint install_backend_dependencies install_test_dependencies coverage
