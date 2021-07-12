.PHONY: clean upload format

dist:
	pipenv run python -m build

clean:
	rm -rf dist *.egg-info

upload: dist
	pipenv run python -m twine upload --repository pypi dist/*

format:
	pipenv run python -m black termimg

