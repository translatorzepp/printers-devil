# Printer's Devil

A rough-and-ready python app to download content from a website and turn it into a .epub ebook.

This is based on the EPUB 3.2 schema.

## Instructions

* In `main.py`:
	* set `TITLE` and `TABLE_OF_CONTENTS_LINK`
	* in `chapter_links_div()`, specify criteria for an HTML tag that will contain the actual chapter links on the page linked to in `TABLE_OF_CONTENTS_LINK`
	* modify handling of each chapter `link` if need be
* In `epubwriter.py`:
	* fill out metadata in `write_rootfile()`
	* modify the `CHAPTER_NUMBER_PATTERN` if need be
* Place a `cover.jpeg` file to act as the cover in the same directory as these files.

To run it:

`python3 main.py`

Now, because this isn't 100% finished: you will need to zip up the resulting files as a .epub file. See commands notated in `make()` in `epubwriter.py`.

