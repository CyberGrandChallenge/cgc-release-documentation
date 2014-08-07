DOC_DIR		 = $(DESTDIR)/usr/share/cgc-docs/
HOWTO_DIR 	 = $(DOC_DIR)/walk-throughs

all: 
	echo nothing to see here

html:
	@for doc in walk-throughs/*.md ; do pandoc -s -t html -o $$doc.html $$doc ; done

install:
	install -d $(DOC_DIR)
	install -d $(HOWTO_DIR)
	install -m 444 replay.dtd $(DOC_DIR)
	install -m 444 pov-markup-spec.txt $(DOC_DIR)
	install -m 444 *.pdf $(DOC_DIR)
	install -m 444 walk-throughs/*.md $(HOWTO_DIR)

clean:
	echo nothing to see here either
