mainDir := $(shell pwd)

run: libs/python
	export LD_LIBRARY_PATH=$(mainDir)/libs/libgit2/libgit2-0.27.0/installed/lib;\
	export PYTHONPATH=$(mainDir)/libs/python:${PYTHONPATH};\
	export LIBGIT2=$(mainDir)/libs/libgit2/libgit2-0.27.0/installed/;\
	python3 main.py

libs/libgit2: libs
	cd $(mainDir)/libs;\
	mkdir libgit2;\
	cd libgit2;\
	wget https://github.com/libgit2/libgit2/archive/v0.27.0.tar.gz;\
	tar xzf v0.27.0.tar.gz;\
	cd libgit2-0.27.0/;\
	cmake . -DCMAKE_INSTALL_PREFIX=$(mainDir)/libs/libgit2/libgit2-0.27.0/installed;\
	make;\
	make install;\
	touch $(mainDir)/libs/libgit2

libs/python: libs libs/libgit2
	mkdir libs/python;\
	export LD_LIBRARY_PATH=$(mainDir)/libs/libgit2/libgit2-0.27.0/installed/lib;\
	export LIBGIT2=$(mainDir)/libs/libgit2/libgit2-0.27.0/installed/;\
	export PYTHONPATH=$(mainDir)/libs/python:${PYTHONPATH};\
	cd libs;\
	curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py;\
	python3 get-pip.py --user;\
	cd ..;\
	~/.local/bin/pip3 install -t libs/python -r dependencies
	touch $(mainDir)/libs/python

libs: dependencies.md5
	mkdir libs;\
	rm -r libs;\
	mkdir libs

dependencies.md5: dependencies
	@md5sum $< | cmp -s $@ -; if test $$? -ne 0; then md5sum $< > $@; fi
clean:
	rm -r libs
