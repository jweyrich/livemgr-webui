from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
	def __init__(self, *args, **kwargs):
		canvas.Canvas.__init__(self, *args, **kwargs)
		self._saved_page_states = []
	def showPage(self):
		self._saved_page_states.append(dict(self.__dict__))
		self._startPage()
	def save(self):
		"""Add page info to each page (page x of y)"""
		num_pages = len(self._saved_page_states)
		for state in self._saved_page_states:
			self.__dict__.update(state)
			self.drawPageNumber(num_pages)
			canvas.Canvas.showPage(self)
		canvas.Canvas.save(self)
	def drawPageNumber(self, page_count):
		"""Derived classes must implement it"""
		pass

def coord_tl(pagesize, x, y):
	return x, pagesize[1] - y
def coord_tr(pagesize, x, y):
	return pagesize[0] - x, pagesize[1] - y
