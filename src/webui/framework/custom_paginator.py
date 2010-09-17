from django.core.paginator import Paginator, InvalidPage, EmptyPage

#class Callable:
#	def __init__(self, anycallable):
#		self.__call__ = anycallable
#	get_page = Callable(get_page)
#	paginate = Callable(paginate)

class CustomPaginator(Paginator):
	def __init__(self, request, queryset, per_page=25, page_number=None):
		Paginator.__init__(self, queryset, per_page or 10)
		if page_number == None:
			page_number = self._page_from_request(request)
		self.page = self._paginate(page_number)
	def _paginate(self, page_number):
		try:
			result = self.page(page_number)
		except (EmptyPage, InvalidPage):
			result = self.page(self.num_pages)
		self._limited_page_range(page_number, 5)
		return result
	def _page_from_request(self, request):
		try:
			page = int(request.GET.get('page', '1'))
		except ValueError:
			page = 1
		return page
	def _limited_page_range(self, page_number, range_gap=5):
		start = page_number - range_gap
		if start < range_gap:
			start = 1
			end = start + range_gap * 2 + 1
			if end > self.num_pages:
				end = self.num_pages + 1
		else:
			if page_number < self.num_pages - range_gap:
				end = page_number + range_gap + 1
			else:
				end = self.num_pages + 1
		self.limited_page_range = range(start, end)
