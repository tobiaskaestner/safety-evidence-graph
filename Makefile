.PHONY: test lint docs docs-live clean

test:
	pytest

lint:
	ruff check .

docs:
	python -m doc build

docs-live:
	python -m doc live manual

clean:
	python -m doc clean
	rm -rf build dist
