BBSLIST = ibbs1015.zip

all: fonebook.txt

fonebook.txt: ibbs/syncterm.lst
	python sync2qodem.py -o $@ $^

ibbs/syncterm.lst: $(BBSLIST)
	mkdir ibbs
	(cd ibbs; unzip ../$(BBSLIST))

clean:
	rm -rf ibbs
	rm -f fonebook.txt

