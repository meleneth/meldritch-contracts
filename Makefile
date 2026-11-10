.PHONY: check generate package clean

check:
	python3 tools/validate/validate.py
	python3 tools/generate/generate.py --check

generate:
	python3 tools/generate/generate.py

package: check
	python3 tools/package.py

clean:
	rm -rf dist
