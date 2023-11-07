SHELL = /bin/bash


help:
	poetry run python main.py -h

install:
	poetry install
	cp .env.example .env

install_dev:
	poetry install --with dev
	cp .env.example .env

check: install_dev
	poetry run ruff check . --config ruff.toml

test: install_dev
	docker pull python
	poetry run pytest
