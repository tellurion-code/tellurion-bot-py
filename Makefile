mainDir := $(shell pwd)

run: storage/libs/python storage/libs/finaltouch
	cd $(mainDir);\
	export LD_LIBRARY_PATH=$(mainDir)/storage/libs/libgit2/libgit2-0.27.0/installed/lib;\
	export PYTHONPATH=$(mainDir)/storage/libs/python:${PYTHONPATH};\
	export LIBGIT2=$(mainDir)/storage/libs/libgit2/libgit2-0.27.0/installed/;\
	python3 -u main.py
storage/libs/finaltouch: storage/libs/python
	touch storage/libs/python storage/libs/get-pip.py
storage/libs/libgit2: storage/libs
	cd $(mainDir);\
	cd $(mainDir)/storage/libs;\
	mkdir libgit2;\
	cd libgit2;\
	wget https://github.com/libgit2/libgit2/archive/v0.27.0.tar.gz;\
	tar xzf v0.27.0.tar.gz;\
	cd libgit2-0.27.0/;\
	cmake . -DCMAKE_INSTALL_PREFIX=$(mainDir)/storage/libs/libgit2/libgit2-0.27.0/installed;\
	make;\
	make install;\
	touch $(mainDir)/storage/libs/libgit2

storage/libs/get-pip.py: storage/libs
	cd $(mainDir);\
	cd storage/libs;\
	curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py;\
	export PYTHONPATH=$(mainDir)/storage/libs/python:${PYTHONPATH};\
	python3 get-pip.py --user

storage/libs/python: storage/libs storage/libs/get-pip.py storage/libs/dependencies.sha512
	cd $(mainDir);\
	mkdir storage/libs/python;\
	rm -r storage/libs/python;\
	mkdir storage/libs/python;\
	export LD_LIBRARY_PATH=$(mainDir)/storage/libs/libgit2/libgit2-0.27.0/installed/lib;\
	export LIBGIT2=$(mainDir)/storage/libs/libgit2/libgit2-0.27.0/installed/;\
	export PYTHONPATH=$(mainDir)/storage/libs/python:${PYTHONPATH};\
	~/.local/bin/pip3 install -U -t storage/libs/python -r dependencies
	touch $(mainDir)/storage/libs/python
storage:
	cd $(mainDir);\
	mkdir storage;\
	echo .
storage/libs: storage
	cd $(mainDir);\
	mkdir storage/libs;\
	echo .

storage/libs/dependencies.sha512: dependencies storage/libs
	cd $(mainDir);\
	sha512sum $< | cmp -s $@ -; if test $$? -ne 0; then sha512sum $< > $@; fi

clean:
	cd $(mainDir);\
	rm -r storage
