from datetime import date, datetime
from time import localtime, mktime

def adjust_date(value, add_one_day=False):
	#timestamp = strptime(value, "%d/%m/%Y")
	assert isinstance(value, date)
	timestamp = value.timetuple()
	if add_one_day:
		epoch = mktime(timestamp)
		timestamp = localtime(epoch + 86399) # 23h59m59s
	return datetime(*timestamp[:6])
