.PHONY: check generate package clean

check:
	python3 tools/validate/validate.py
	python3 tools/generate/generate.py --check
	python3 tools/integrate.py --help >/dev/null
	bash -n bin/_integration-common.sh bin/verify bin/build bin/test bin/run bin/full-check

generate:
	python3 tools/generate/generate.py

package: check
	python3 tools/package.py

clean:
	rm -rf dist
