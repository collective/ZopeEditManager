.PHONY: build
build:
	 rm -rf dist build
	 python setup.py py2app

.PHONY: build-dev
build-dev:
	 rm -rf dist build
	 python setup.py py2app -A

.PHONY: debug
debug:
	./dist/ZopeEditManager.app/Contents/MacOS/ZopeEditManager
