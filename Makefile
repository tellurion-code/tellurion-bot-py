mainDir := $(shell pwd)

run: storage/libs/python3.6 storage/libs/finaltouch
	cd $(mainDir);\
	export LD_LIBRARY_PATH=$(mainDir)/storage/libs/libgit2/libgit2-0.27.0/installed/lib;\
	export PYTHONPATH=$(mainDir)/storage/libs/python3.6:${PYTHONPATH};\
	export LIBGIT2=$(mainDir)/storage/libs/libgit2/libgit2-0.27.0/installed/;\
	python3.6 -u main.py
python3.6: storage/libs/python3.6 storage/libs/finaltouch
	cd $(mainDir);\
	export LD_LIBRARY_PATH=$(mainDir)/storage/libs/libgit2/libgit2-0.27.0/installed/lib;\
	export PYTHONPATH=$(mainDir)/storage/libs/python3.6:${PYTHONPATH};\
	export LIBGIT2=$(mainDir)/storage/libs/libgit2/libgit2-0.27.0/installed/;\
	python3.6
storage/libs/finaltouch: storage/libs/python3.6
	touch storage/libs/python3.6 storage/libs/get-pip.py
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
	export PYTHONPATH=$(mainDir)/storage/libs/python3.6:${PYTHONPATH};\
	python3.6 get-pip.py --user

storage/libs/python3.6: storage/libs storage/libs/get-pip.py storage/libs/dependencies.sha512
	cd $(mainDir);\
	mkdir storage/libs/python3.6;\
	rm -r storage/libs/python3.6;\
	mkdir storage/libs/python3.6;\
	export LD_LIBRARY_PATH=$(mainDir)/storage/libs/libgit2/libgit2-0.27.0/installed/lib;\
	export LIBGIT2=$(mainDir)/storage/libs/libgit2/libgit2-0.27.0/installed/;\
	export PYTHONPATH=$(mainDir)/storage/libs/python3.6:${PYTHONPATH};\
	~/.local/bin/pip3 install -U -t storage/libs/python3.6 -r dependencies
	touch $(mainDir)/storage/libs/python3.6
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
