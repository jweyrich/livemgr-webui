from StringIO import StringIO
from django import forms
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _, ugettext_lazy
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.platypus.flowables import Spacer
from reportlab.platypus.paragraph import Paragraph
from webui.common import CustomPaginator
from webui.common.color_dict import color_dict
from webui.common.decorators.rest import rest_multiple, rest_get
from webui.common.http import method
from webui.common.report import coord_tl, NumberedCanvas, coord_tr
from webui.imdata.models import Message
from webui.imdata.models.profile import Profile
from webui.imdata.models.view_messages import ViewMessages
from webui.imdata.utils.formatters import ip_long_to_str
from webui.imdata.utils.local_datetime import adjust_date
import django_tables as tables

class ViewMessagesTable(tables.ModelTable):
	class Meta:
		model = ViewMessages
		exclude = ['id', 'content', 'inbound', 'is_active', 'localuser_id', 'filtered', 'clientip']
	# Use ugettext_lazy because class definitions are evaluated once!
	conversation_id = tables.Column(name='conversation_id', visible=False)
	timestamp = tables.Column(verbose_name=ugettext_lazy("timestamp"))
	localim = tables.Column(verbose_name=ugettext_lazy("user"))
	remoteim = tables.Column(verbose_name=ugettext_lazy("buddy"))
	#is_active = tables.Column(verbose_name=ugettext_lazy("Active"))
	def __init__(self, request, *args, **kwargs):
		super(ViewMessagesTable, self).__init__(*args, **kwargs)
		self.see_users = request.user.has_perm('see_users')
	def render_localim(self, instance):
		# TODO(jweyrich): should we care about XSS on localim?
		if self.see_users:
			return mark_safe('<a href="%s">%s</a>' % (
				reverse('imdata:users-edit', args=[instance.localuser_id]),
				instance.localim))
		else:
			return mark_safe(instance.localim)
	def render_timestamp(self, instance):
		return instance.timestamp.strftime(_('%m/%d/%Y - %I:%M:%S %p'))

#class MyDateInput(forms.DateInput):
#	raw_html = u'''
#		<div class="datepicker">
#			&nbsp;<a href="javascript:CalendarUtil.dateNow('#id_%(name)s');" style="text-decoration: none;">Today</a>
#			&nbsp;|&nbsp;
#			<img src="/media/img/django/icon_calendar.gif" style="vertical-align: middle; cursor: pointer;">
#		</div>
#	'''
#	def __init__(self, *args, **kwargs):
#		super(MyDateInput, self).__init__(*args, **kwargs)
#	def render(self, name, value, attrs=None):
#		if value is None: value = ''
#		final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
#		input = u'<input%s />' % forms.util.flatatt(final_attrs)
#		div = self.raw_html % {'name': name}
#		return mark_safe(input + div)

class ViewMessagesSearchForm(forms.Form):
	message = forms.CharField(required=False, label=ugettext_lazy("message"))
	localim = forms.CharField(required=False, label=ugettext_lazy("user"))
	remoteim = forms.CharField(required=False, label=ugettext_lazy("buddy"))
	filtered = forms.BooleanField(required=False, label=ugettext_lazy("filtered"),
		widget=forms.CheckboxInput(attrs={
			'style': 'float: left; clear: right;',
		})
	)
	from_date = forms.DateField(required=False,
		label=ugettext_lazy("from date"),
		widget=forms.DateInput(attrs={
			'class': 'datepicker',
			'format': ugettext_lazy('mm/dd/yyyy'),
			#'title': ugettext_lazy("From date"),
			#'maxlength': '10',
			#'style': 'float: left; position: relative; z-index: 1;',
		}))
	to_date = forms.DateField(required=False,
		label=ugettext_lazy("to date"),
		widget=forms.DateInput(attrs={
			'class': 'datepicker',
			'format': ugettext_lazy('mm/dd/yyyy')
		}))


@rest_multiple([method.GET, method.POST])
@login_required
@permission_required('imdata.see_conversation')
def index(request):
	if request.method == method.GET:
		qset = ViewMessages.objects.all().exclude(conversation_id=0)
	elif request.method == method.POST:
		per_page = request.POST.get('per_page')
		if per_page != None:
			Profile.objects.filter(user=request.user).update(per_page_conversations=per_page)
			return HttpResponse()
		form = ViewMessagesSearchForm(request.POST)
		if not form.is_valid():
			return HttpResponseBadRequest(_('Invalid search criteria'))
		values = form.cleaned_data
		#print values
		try:
			if values['to_date']:
				values['to_date'] = adjust_date(values['to_date'], True)
		except ValueError:
			return HttpResponseBadRequest(_('Invalid date'))
		qset = ViewMessages.objects.all()
		if values['from_date']:
			qset = qset.filter(timestamp__gte=values['from_date'])
		if values['to_date']:
			qset = qset.filter(timestamp__lte=values['to_date'])
		if values['message']:
			qset = qset.filter(content__icontains=values['message'])
		if values['localim']:
			qset = qset.filter(localim__icontains=values['localim'])
#			qset = qset.filter(
#				(Q(inbound = False) & Q(localim__icontains = values['localim'])) |
#				(Q(inbound = True) & Q(remoteim__icontains = values['localim']))
#			)
		if values['remoteim']:
			qset = qset.filter(remoteim__icontains=values['remoteim'])
#			qset = qset.filter(
#				(Q(inbound = True) & Q(localim__icontains = values['remoteim'])) |
#				(Q(inbound = False) & Q(remoteim__icontains = values['remoteim']))
#			)
		if values['filtered']:
			qset = qset.filter(filtered=values['filtered'])
	qset.query.group_by = ['conversation_id']
	profile = request.user.get_profile()
	order_by = request.GET.get('sort', '-timestamp')
	table = ViewMessagesTable(request, qset, order_by=order_by)
	#
	# DO NOT REMOVE NOR MOVE
	#
	print 'Found %i' % len(table.data)
	paginator = CustomPaginator(request, table.rows, profile.per_page_conversations)
	context_instance = RequestContext(request)
	template_name = 'conversations/list.html'
	extra_context = {
		'menu': 'conversations',
		'table': table,
		'paginator': paginator,
		'search_form': ViewMessagesSearchForm()
	}
	return render_to_response(template_name, extra_context, context_instance)

@rest_get
@login_required
@permission_required('imdata.see_conversation')
def show(request, object_id):
#	if not request.is_ajax():
#		return HttpResponseNotAllowed('Invalid request (use ajax)')
	object_id = long(object_id)
	if object_id is None:
		return HttpResponseBadRequest(_("Missing argument: %s") % 'object_id')
	messages = Message.objects \
		.filter(conversation_id=object_id) \
		.order_by('timestamp')
	if not messages:
		#return HttpResponseBadRequest(_('Conversation not found'))
		raise Http404('No %s matches the given query.' % 'Message')
	messages[0].clientip = ip_long_to_str(messages[0].clientip)
	context_instance = RequestContext(request)
	template_name = 'conversations/show.html'
	extra_context = {
		'first_message': messages[0],
		'messages': messages,
		'colors': color_dict()
	}
	return render_to_response(template_name, extra_context, context_instance)

@rest_get
@login_required
@permission_required('imdata.see_conversation')
def report_pdf(request, object_id):
	object_id = long(object_id)
	if object_id is None:
		return HttpResponseBadRequest(_("Missing argument: %s") % 'object_id')
	messages = Message.objects \
		.filter(conversation_id=object_id) \
		.order_by('timestamp')
	if not messages:
		return HttpResponseBadRequest(_('Conversation not found'))
	messages[0].clientip = ip_long_to_str(messages[0].clientip)

	# START
	styles = getSampleStyleSheet()
	buffer = StringIO()
	PAGESIZE = A4

	def renderHeader(canvas, doc):
		def paraFromHeader(key, value):
			return Paragraph('<strong>%s</strong>: %s' % (key, value), styles['Normal'])
		def paraFromHeader2(key1, value1, key2, value2):
			return Paragraph('<strong>%s</strong>: %s <strong>%s</strong>: %s'
				% (key1, value1, key2, value2), styles['Normal'])
#		def renderPageNumber(canvas):
#			x, y = coord_tr(PAGESIZE, 1.5*cm, 1,5*cm)
#			canvas.setFont('Helvetica', 10)
#			canvas.drawRightString(x, y,
#				_('Page %(this)i of %(total)i') % canvas.getPageNumber(), 0)
		canvas.saveState()
		flowables = []
		flowables.append(paraFromHeader(_('Conversation'), '#%i' % messages[0].conversation_id))
		flowables.append(paraFromHeader2(_('User'), messages[0].localim, 'IP', messages[0].clientip))
		flowables.append(paraFromHeader(_('Buddy'), messages[0].remoteim))
		flowables.append(paraFromHeader(_('Started in'), messages[0].timestamp.strftime(_("%m/%d/%Y - %I:%M:%S %p"))))
		flowables.append(paraFromHeader(_('Total messages'), '%i' % len(messages)))
		flowables.append(Spacer(0, 0.5 * cm))
		x, y = coord_tl(PAGESIZE, 1.5 * cm, 1.5 * cm)
		#renderPageNumber(canvas)
		for f in flowables:
			f.wrap(PAGESIZE[0], PAGESIZE[1])
			f.drawOn(canvas, x, y)
			y -= f.height
		canvas.restoreState()

	class ReportCanvas(NumberedCanvas):
		def __init__(self, *args, **kwargs):
			NumberedCanvas.__init__(self, *args, **kwargs)
			self.setAuthor('')
			self.setTitle('')
			self.setSubject('')
			self.setKeywords('')
			#self.setEncrypt()
			self.setFont('Helvetica', 12)
		def drawPageNumber(self, page_count):
			self.setFont("Helvetica", 9)
			x, y = coord_tr(self._pagesize, 1.5 * cm, 1.5 * cm)
			self.drawRightString(x, y,
				_("Page %(this)i of %(total)i") % {
					'this': self._pageNumber,
					'total': page_count
				}
			)

	def format_default(msg, colors):
		time = msg.timestamp.strftime(_('%m/%d/%Y %I:%M:%S %p'))
		if not msg.inbound:
			sender = '<font color="' + colors.get(msg.localim) + '">' + msg.localim + '</font>'
		else:
			sender = '<font color="' + colors.get(msg.remoteim) + '">' + msg.remoteim + '</font>'
		text = '<strong>' + time + ' - ' + sender + '</strong>'
		if msg.filtered:
			return text + ': <font color="red"><b>[x]</b></font> ' + msg.content
		else:
			return text + ': ' + msg.content
	def para_from_message(msg, colors):
		formatters = {
			Message.Type.UNKNOWN: format_default,
			Message.Type.MSG: format_default,
			Message.Type.FILE: format_default,
			Message.Type.TYPING: format_default,
			Message.Type.CAPS: format_default,
			Message.Type.WEBCAM: format_default,
			Message.Type.REMOTEDESKTOP: format_default,
			Message.Type.APPLICATION: format_default,
			Message.Type.EMOTICON: format_default,
			Message.Type.INK: format_default,
			Message.Type.NUDGE: format_default,
			Message.Type.WINK: format_default,
			Message.Type.VOICECLIP: format_default,
			Message.Type.GAMES: format_default,
			Message.Type.PHOTO: format_default,
		}
		text = formatters.get(msg.type, lambda x: None)(msg, colors)
		return Paragraph(text, styles['Normal'])
	contents = []
	colors = color_dict()
	# force localim and remoteim colors
	if len(messages) > 0:
		colors.get(messages[0].localim)
		colors.get(messages[0].remoteim)
	for msg in messages:
		contents.append(para_from_message(msg, colors))

	doc = SimpleDocTemplate(buffer, pagesize=PAGESIZE,
		rightMargin=1.5 * cm, leftMargin=1.3 * cm,
		topMargin=3.5 * cm, bottomMargin=1.5 * cm)
	doc.build(
		contents,
		onFirstPage=renderHeader,
		onLaterPages=renderHeader,
		canvasmaker=ReportCanvas
	)

	response = HttpResponse(buffer.getvalue(), mimetype='application/pdf')
	response['Content-Disposition'] = 'attachment; filename=report-%i.pdf' % object_id
	buffer.close()
	return response
