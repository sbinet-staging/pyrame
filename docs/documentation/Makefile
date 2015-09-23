all: doc

prepare:
	if test -d src; then rm -rf src; fi
	mkdir src
	cp conf.py src
	cp base_add_doc_path.py src/add_doc_path.py
	cp index.rst src
	for i in `find ../.. -name '*.rst' | grep -v "docs"`; do /bin/cp -f $$i src/; echo "sys.path.append(\""`dirname $$i`"\")" >> src/add_doc_path.py; done
	for i in `find ../.. -name '*.doc.svg' | grep -v "docs"`; do /bin/cp -f $$i src/; done
	for i in `find ../.. -name '*.doc.png' | grep -v "docs"`; do /bin/cp -f $$i src/; done
	for i in `find . -maxdepth 1 -name '*.rst'`; do cp $$i src; done
	for i in `find . -maxdepth 1 -name '*.doc.svg'`; do cp $$i src; done
	for i in `find . -maxdepth 1 -name '*.doc.png'`; do cp $$i src; done

doc: prepare
	sphinx-build -W -b html src html 2>&1

clean:
	rm -rf html src *.pyc __pycache__ 

install: 
	cp -rf html/* /opt/pyrame/doc 2>&1 

uninstall:
