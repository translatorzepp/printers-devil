import os
import re
from shutil import copyfile
from chapter import Chapter

#.
#├── EPUB
#│   ├── book.opf
#│   ├── cover.jpeg
#│   ├── cover.xhtml
#│   ├── CHAPTERS
#│   │   ├── nav.xhtml
#│   │   └── chapter1.xhtml
#├── META-INF
#│   └── container.xml
#└── mimetype

class Ebook:
	content_directory = "EPUB"
	chapters_directory = "CHAPTERS"
	meta_directory = "META-INF"

	rootfile_path_name = str()
	title = str()
	base_name = str()
	chapters = []

	CHAPTER_NUMBER_PATTERN = re.compile(f"Chapter_([\d.]+\d*)")
	# TODO: verify that this matches on "Chapter_115.2_something.xhtml" AND "Chapter_100.xhtml"


	def __init__(self, title, base_name, chapters):
		self.title = title
		self.base_name = base_name
		self.chapters = chapters
		self.rootfile_path_name = os.path.join(self.content_directory, f"{self.base_name}.opf")


	def common_start_xhtml(self):
		return f"""<?xml version="1.0" encoding="UTF-8"?>
<html xml:lang="en-us" lang="en-us" xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xmlns:ns="http://www.w3.org/2001/10/synthesis">
<head>
	<title>{self.title}</title>
</head>
<body>
		"""


	def common_end_xhtml(self):
		return "</body>\n</html>"


	def make_directory_structure(self):
		os.mkdir(self.base_name)
		os.mkdir(os.path.join(self.base_name, self.meta_directory))

		os.mkdir(os.path.join(self.base_name, self.content_directory))
		os.mkdir(os.path.join(self.base_name, self.content_directory, self.chapters_directory))


	def write_mimetype(self):
		with open(os.path.join(self.base_name, "mimetype"), "w") as f:
			f.write("application/epub+zip")


	def write_container(self):
		container_contents = f"""<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
	<rootfiles>
		<rootfile full-path="{self.rootfile_path_name}" media-type="application/oebps-package+xml"/>
	</rootfiles>
</container>
		"""
		with open(os.path.join(self.base_name, self.meta_directory, "container.xml"), "w") as f:
			f.write(container_contents)


	def write_cover(self):
		cover = '<div class="cover"><img src="cover.jpeg" alt="Image"/></div>'

		with open(os.path.join(self.base_name, self.content_directory, "cover.xhtml"), "w") as f:
			f.write(self.common_start_xhtml())
			f.write(cover)
			f.write(self.common_end_xhtml())


	def write_chapter_files(self):
		for chapter in self.chapters:
			with open(os.path.join(self.base_name, self.content_directory, self.chapters_directory, f"{chapter.sanitized_filename()}.xhtml"), "w") as f:
				f.write(self.common_start_xhtml())
				f.write(chapter.contents)
				f.write(self.common_end_xhtml())


	def _generate_table_of_contents(self):
		chapter_list_items = []
		for chapter in self.chapters:
			chapter_list_items.append(f'<li><a href="{self.chapters_directory}/{chapter.sanitized_filename()}.xhtml">{chapter.title}</a></li>')

		return '\n\t<nav epub:type="toc">\n\t\t<h2>Chapters</h2>\n\t\t<ol epub:type="list">' + "\n\t\t".join(chapter_list_items) + "\n\t\t</ol>\n\t</nav>\n"


	def write_nav(self):
		with open(os.path.join(self.base_name, self.content_directory, "nav.xhtml"), "w") as f:
			f.write(self.common_start_xhtml())
			f.write(self._generate_table_of_contents())
			f.write(self.common_end_xhtml())


	def _id_from_filename(self, filename):
		chapter_number = self.CHAPTER_NUMBER_PATTERN.search(filename)
		if chapter_number:
			return f"chapter{chapter_number.group(1)}"
		else:
			print(f"ERROR: Did not find chapter number in filename: {filename}")
			return filename


	def _generate_manifest(self, chapters):
		items = ['<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>', '<item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>']
		for chapter in chapters:
			id = self._id_from_filename(chapter)
			items.append(f'<item id="{id}" href="{self.chapters_directory}/{chapter}" media-type="application/xhtml+xml"/>')
		items.append(f'<item id="cover-image" href="cover.jpeg" media-type="image/jpeg"/>')
		return '\n\t<manifest>\n\t\t' + "\n\t\t".join(items) + '\n\t</manifest>'


	def _generate_spine(self, chapters):
		items = ['<itemref idref="cover"/>']
		for chapter in chapters:
			id = self._id_from_filename(chapter)
			items.append(f'<itemref idref="{id}"/>')
		return '\n\t<spine>\n\t\t' + "\n\t\t".join(items) + '\n\t</spine>'


	def _generate_file_name_list(self):
		filenames = []
		for chapter in self.chapters:
			filenames.append(f"{chapter.sanitized_filename()}.xhtml")
		return filenames


	def write_rootfile(self):
		chapters_filenames = self._generate_file_name_list()

		header = '<?xml version="1.0" encoding="UTF-8"?>'
		package_open = '\n<package xmlns="http://www.idpf.org/2007/opf" version="3.0" xml:lang="en" unique-identifier="auniqueidforepub">'
		# TODO: source metadata from config file or something
		metadata = """<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
	<dc:title>Title of the Book</dc:title>
	<dc:creator>An Onymous</dc:creator>
	<dc:date>2016</dc:date>
	<meta property="dcterms:modified">YYYY-MM-DDT00:00:00Z</meta>
	<dc:identifier id="auniqueidforepub">auniqueidforepub</dc:identifier>
	<dc:format>X pages or chapters</dc:format>
	<dc:type>Text</dc:type>
	<dc:language>en</dc:language>
	<dc:rights>I own nothing. Also: don't like, don't read!</dc:rights>
	<dc:publisher></dc:publisher>
</metadata>
		"""
		# TODO: try to figure out how to add extra metadata
		manifest = self._generate_manifest(chapters_filenames)
		spine = self._generate_spine(chapters_filenames)
		package_close = "\n</package>"

		with open(os.path.join(self.base_name, self.rootfile_path_name), "w") as f:
			f.write(header)
			f.write(package_open)
			f.write(metadata)
			f.write(manifest)
			f.write(spine)
			f.write(package_close)


	def make(self):
		print("******* making epub format ebook... *********")
		self.make_directory_structure()

		self.write_mimetype()
		self.write_container()
		self.write_rootfile()

		self.write_nav()
		self.write_cover()
		self.write_chapter_files()

		# Make sure cover.jpeg is in the same directory
		copyfile(os.path.join("cover.jpeg"), os.path.join(self.base_name, self.content_directory, "cover.jpeg"))

		# TODO: add zip commands--equivalent of:
		# cd <base_name> && zip -X ../<base_name>.epub -0 mimetype && zip -rg ../<base_name>.epub META-INF/ -x \*.DS_Store && zip -rg ../<base_name>.epub EPUB/ -x \*.DS_Store

		# maybe TODO: incorporate epubcheck and run it against newly-created book: java -jar epubcheck-4.2.4/epubcheck.jar <base_name>.epub
