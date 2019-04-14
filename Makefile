.PHONY: test clean clean-pyc clean-build help
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python3 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

test: ## run pytest
	docker-compose run web pytest

mmgs: ## make migrations
	docker-compose run web python3 manage.py makemigrations

mg: ## migrate
	docker-compose run web python3 manage.py migrate

up: ## run the django test webserver
	docker-compose up

shell: ## run a shell with the app model's imported
	docker-compose run web python3 manage.py shell

build: ## rebuild the docker container
	docker-compose up --build

down: ## shutdown any running docker instances
	docker-compose down

static: ## run the "collectstatic" command
	docker-compose run web python manage.py collectstatic

clean: clean-build clean-pyc ## remove all build, test, coverage and Python artifacts

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	rm -fr .cache/
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

heroku: mmgs ## update the code on heroku
	cp -r ./* ../heroku_core && git status
