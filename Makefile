DOC_DIR		 = $(DESTDIR)/usr/share/cgc-docs/
HOWTO_DIR 	 = $(DOC_DIR)/walk-throughs
NEWSLETTER_DIR 	 = $(DOC_DIR)/newsletter
SCRIPTS_DIR = $(DOC_DIR)/scripts

all: 
	echo nothing to see here

html:
	@for doc in walk-throughs/*.md ; do pandoc -s -t html -o $$doc.html $$doc ; done
	@for doc in newsletter/*.md ; do pandoc -s -t html -o $$doc.html $$doc ; done

install:
	install -d $(DOC_DIR)
	install -d $(HOWTO_DIR)
	install -d $(NEWSLETTER_DIR)
	install -d $(SCRIPTS_DIR)
	install -m 444 replay.dtd $(DOC_DIR)
	install -m 444 pov-markup-spec.txt $(DOC_DIR)
	install -m 444 *.pdf $(DOC_DIR)
	install -m 444 walk-throughs/*.md walk-throughs/*.pdf $(HOWTO_DIR)
	install -m 444 newsletter/*.md $(NEWSLETTER_DIR)
	install -m 444 scripts/*.py $(SCRIPTS_DIR)

clean:
	echo nothing to see here either
