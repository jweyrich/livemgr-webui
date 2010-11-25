from StringIO import StringIO
from django import forms
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseBadRequest, HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import filesizeformat
from django.utils.html import escape
from django.utils.translation import ugettext as _, ugettext_lazy
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.platypus.flowables import Spacer
from reportlab.platypus.paragraph import Paragraph
from webui.common import CustomPaginator
from webui.common.color_dict import color_dict
from webui.common.decorators.rest import rest_multiple, rest_get
from webui.common.http import method
from webui.common.report import coord_tl, NumberedCanvas, coord_tr
from webui.livemgr.models import Message
from webui.livemgr.models.profile import Profile
from webui.livemgr.utils.formatters import ip_long_to_str
from webui.livemgr.utils.local_datetime import adjust_date
import django_tables as tables

class MessageTable(tables.ModelTable):
	class Meta:
		model = Message
		#exclude = ['id', 'content', 'inbound', 'is_active', 'localuser_id', 'filtered', 'clientip']
		columns = ['conversation_id', 'timestamp', 'localim', 'remoteim']
	# Use ugettext_lazy because class definitions are evaluated once!
	conversation_id = tables.Column(name='conversation_id', visible=False)
	def render_timestamp(self, instance):
		return instance.timestamp.strftime(_('%m/%d/%Y - %I:%M:%S %p'))

class MessageSearchForm(forms.Form):
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
@permission_required('livemgr.see_conversation')
def index(request):
	if request.method == method.GET:
		qset = Message.objects.all()
	elif request.method == method.POST:
		per_page = request.POST.get('per_page')
		if per_page != None:
			Profile.objects.filter(user=request.user).update(per_page_conversations=per_page)
			return HttpResponse()
		form = MessageSearchForm(request.POST)
		if not form.is_valid():
			return HttpResponseBadRequest(_('Invalid search criteria'))
		values = form.cleaned_data
		try:
			if values['to_date']:
				values['to_date'] = adjust_date(values['to_date'], True)
		except ValueError:
			return HttpResponseBadRequest(_('Invalid date'))
		qset = Message.objects.all()
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
	profile = request.user.get_profile()
	order_by = request.GET.get('sort', '-timestamp')
	result = CustomPaginator(qset) \
		.instantiate(MessageTable, qset, order_by=order_by) \
		.with_request(request) \
		.group_by(True, 'conversation_id')
	page = result.page(None, profile.per_page_conversations)
	context_instance = RequestContext(request)
	template_name = 'conversations/list.html'
	extra_context = {
		'menu': 'conversations',
		'table': result.instance,
		'page': page,
		'search_form': MessageSearchForm()
	}
	return render_to_response(template_name, extra_context, context_instance)

@rest_get
@login_required
@permission_required('livemgr.see_conversation')
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
@permission_required('livemgr.see_conversation')
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

	# PDF generation
	styles = getSampleStyleSheet()
	styles.add(ParagraphStyle(name='Header',
		alignment=TA_JUSTIFY,
		parent=styles['Normal'],
		fontName='Times-Roman',
		fontSize=10,
		leading=11,
		firstLineIndent=0,
		leftIndent=0))
	styles.add(ParagraphStyle(name='Message',
		alignment=TA_JUSTIFY,
		parent=styles['Normal'],
		fontName='Times-Roman',
		fontSize=10,
		leading=11,
		firstLineIndent=0,
		leftIndent=0))
	buffer = StringIO()
	PAGESIZE = A4

	def renderHeader(canvas, doc):
		def headerPara(key, value):
			return Paragraph('<strong>%s</strong>: %s' % (key, value), styles['Header'])
		def headerPara2(key1, value1, key2, value2):
			return Paragraph('<strong>%s</strong>: %s <strong>%s</strong>: %s'
				% (key1, value1, key2, value2), styles['Header'])
#		def renderPageNumber(canvas):
#			x, y = coord_tr(PAGESIZE, 1.5*cm, 1,5*cm)
#			canvas.setFont('Helvetica', 10)
#			canvas.drawRightString(x, y,
#				_('Page %(this)i of %(total)i') % canvas.getPageNumber(), 0)
		canvas.saveState()
		flowables = []
		flowables.append(headerPara(_('Conversation'), '#%i' % messages[0].conversation_id))
		flowables.append(headerPara2(_('User'), messages[0].localim, 'IP', messages[0].clientip))
		flowables.append(headerPara(_('Buddy'), messages[0].remoteim))
		flowables.append(headerPara(_('Started in'), messages[0].timestamp.strftime(_("%m/%d/%Y - %I:%M:%S %p"))))
		flowables.append(headerPara(_('Total messages'), '%i' % len(messages)))
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
		def drawPageNumber(self, page_count):
			self.setFont("Times-Roman", 10)
			x, y = coord_tr(self._pagesize, 1.5 * cm, 1.5 * cm)
			self.drawRightString(x, y,
				_("Page %(this)i of %(total)i") % {
					'this': self._pageNumber,
					'total': page_count
				}
			)

	def format_sender(msg, colors):
		sender = msg.remoteim if msg.inbound else msg.localim
		return '<font color="' + colors.get(sender) + '">' + sender + '</font>'
	def format_prefix(msg, colors):
		time = msg.timestamp.strftime(_('%m/%d/%Y %I:%M:%S %p'))
		sender = format_sender(msg, colors)
		text = '<strong>' + time + ' - ' + sender + '</strong>: '
		if msg.filtered:
			return text + '<font color="red"><b>[x]</b></font> '
		return text
	def format_msg(msg, colors):
		return format_prefix(msg, colors) + escape(msg.content)
	def format_file(msg, colors):
		parts = msg.content.split(' ')
		message = '<b>%s</b>: %s (%s)' % (
			_('File transfer'),
			escape(' '.join(parts[1:])),
			filesizeformat(parts[0])
		)
		return format_prefix(msg, colors) + message
	def format_webcam(msg, colors):
		return format_prefix(msg, colors) + '<b>%s</b>' % _('Video Call')
	def format_remotedesktop(msg, colors):
		return format_prefix(msg, colors) + '<b>%s</b>' % _('Remote Desktop')
	def format_application(msg, colors):
		return format_prefix(msg, colors) + '<b>%s</b>' % _('MSN Activity')
	def format_emoticon(msg, colors):
		return format_prefix(msg, colors) + '<b>%s</b>' % _('Custom emoticon')
	def format_ink(msg, colors):
		return format_prefix(msg, colors) + '<b>%s</b>' % _('Handwriting')
	def format_nudge(msg, colors):
		return format_prefix(msg, colors) + '<b>%s</b>' % _('Nudge')
	def format_wink(msg, colors):
		return format_prefix(msg, colors) + '<b>%s</b>' % _('Wink')
	def format_voiceclip(msg, colors):
		return format_prefix(msg, colors) + '<b>%s</b>' % _('Voice clip')
	def format_games(msg, colors):
		return format_prefix(msg, colors) + '<b>%s</b>' % _('MSN Game')
	def format_photo(msg, colors):
		return format_prefix(msg, colors) + '<b>%s</b>' % _('Photo sharing')
	def messagePara(msg, colors):
		formatters = {
			#Message.Type.UNKNOWN: format_msg,
			Message.Type.MSG: format_msg,
			Message.Type.FILE: format_file,
			#Message.Type.TYPING: format_msg,
			#Message.Type.CAPS: format_msg,
			Message.Type.WEBCAM: format_webcam,
			Message.Type.REMOTEDESKTOP: format_remotedesktop,
			Message.Type.APPLICATION: format_application,
			Message.Type.EMOTICON: format_emoticon,
			Message.Type.INK: format_ink,
			Message.Type.NUDGE: format_nudge,
			Message.Type.WINK: format_wink,
			Message.Type.VOICECLIP: format_voiceclip,
			Message.Type.GAMES: format_games,
			Message.Type.PHOTO: format_photo,
		}
		text = formatters.get(msg.type, lambda x: None)(msg, colors)
		return Paragraph(text, styles['Message'])
	contents = []
	colors = color_dict()
	# Force localim and remoteim colors
	if len(messages) > 0:
		colors.get(messages[0].localim)
		colors.get(messages[0].remoteim)
	for msg in messages:
		contents.append(messagePara(msg, colors))

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
