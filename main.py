import requests
from bs4 import BeautifulSoup
from chapter import Chapter
from epubwriter import Ebook


TITLE = ""
TABLE_OF_CONTENTS_LINK = ""
BASE_NAME = "" # this will be the "root" reference for the book. I recommend a shortened form of the book's title, sans spaces, special characters, etc.


def chapter_links_div(tag):
	return tag.name == "div" and tag.has_attr("class") and tag.has_attr("id") and "lcp_catlist" in tag["class"] and tag["id"] == "lcp_instance_0"


def get_chapters(chapter_links_list):
	chapters = [Chapter(link_tag["title"], link_tag["href"]) for link_tag in chapter_links_list]

	# FOR TESTING ONLY:
	#chapters = chapters[0:2]

	for chapter in chapters:
		response = requests.get(chapter.link)

		print(f"Request to {chapter.link} returned code {response.status_code}")
		if response.status_code == 200:
			chapter_soup = BeautifulSoup(response.text, "html.parser")
			chapter.set_contents(chapter_soup.find(id="wtr-content"))

			#with open(chapter.sanitized_filename() + "xhtml", "w") as f:
			#	f.write(chapter.contents)

		else:
			print(f"Error: {response.content}")

	return chapters


response = requests.get(TABLE_OF_CONTENTS_LINK)
print(f"Request to {TABLE_OF_CONTENTS_LINK} returned code {response.status_code}")
if response.status_code == 200:
	full_table_of_contents_soup = BeautifulSoup(response.text, "html.parser")
	#print(full_table_of_contents_soup)
	table_of_contents_soup = full_table_of_contents_soup.find(chapter_links_div)

	#print(table_of_contents_soup)
	chapters = get_chapters(table_of_contents_soup.find_all("a"))
	ebook = Ebook(TITLE, BASE_NAME, chapters)
	ebook.make()

else:
	print(f"ERROR: {response.content}")
