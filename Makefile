SHELL = /bin/bash


help:
	poetry run python main.py -h

install:
	poetry install

install_dev:
	poetry install --with dev

check: install_dev
	poetry run ruff check . --config ruff.toml

test: install_dev
	docker pull python
	cd tests/
	poetry run pytest .
