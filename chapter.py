class Chapter:
	title = str()
	link = str()
	contents = str()

	def __init__(self, title, link):
		self.title = title
		self.link = link

	def __str__(self):
		return f'{self.title} @ {self.link} : {self.contents[0:13]}'

	def sanitized_filename(self):
		return self.title.replace(":", " -").replace("—", "-").replace("–", "-").replace(" ", "_")
		# TODO: add if title is empty then use the last part of the link instead (^.*.com/(\w+)/?$)

	def set_contents(self, contents):
		self.contents = str(contents)

