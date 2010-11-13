#
# Change these according to your needs
#

CSS_SOURCES = \
	jquery-ui-1.8.6.custom/css/cupertino/jquery-ui-1.8.6.custom.css \
	css/current/theme.css \
	css/current/form.css \
	css/current/search.css \
	css/current/list.css \
	css/current/pagination.css \
	css/current/dashboard.css \
	css/current/login.css \
	css/current/tooltip.css \
	css/current/modal.css

CSS_SOURCES_EXTRA = \
	css/current/specific-moz.css \
	css/current/specific-msie.css \
	css/current/specific-webkit.css

JS_SOURCES = \
	js/i18n.js \
	js/string.format.js \
	js/date.format.js \
	js/calendar.js \
	js/form.js \
	js/search.js \
	js/selection.js \
	js/selectbox.js \
	js/googlecharts.js \
	js/utils.js

JS_SOURCES_EXTRA =

JS_MINIFIED_DEPS = \
	jquery-ui-1.8.6.custom/js/jquery-ui-1.8.6.custom.min.js \
	js/jquery.simplemodal-1.4.1.min.js \
	js/jquery.tools.min.js

CSS_TARGET = css/all.min.css
JS_TARGET = js/all.min.js

#
# Do not change anything below
#

CSS_MINIFIED = $(addsuffix .min.css, $(basename ${CSS_SOURCES}))
JS_MINIFIED = $(addsuffix .min.js, $(basename ${JS_SOURCES}))
CSS_MINIFIED_EXTRA = $(addsuffix .min.css, $(basename ${CSS_SOURCES_EXTRA}))
JS_MINIFIED_EXTRA = $(addsuffix .min.js, $(basename ${JS_SOURCES_EXTRA}))

.PHONY: all clean minify_css concat_css minify_js concat_js

all: minify_css concat_css minify_js concat_js
	@echo Done.

minify_css: $(CSS_MINIFIED) $(CSS_MINIFIED_EXTRA)
minify_js: $(JS_MINIFIED) $(JS_MINIFIED_EXTRA)
concat_css: $(CSS_TARGET)
concat_js: $(JS_TARGET)
	
%.min.css: %.css
	@echo [css] $<
	@java -jar ../../../lib/yuicompressor-2.4.2.jar $< -o $@

%.min.js: %.js
	@echo [js] $<
	@java -jar ../../../lib/yuicompressor-2.4.2.jar $< -o $@

$(CSS_TARGET): $(CSS_MINIFIED)
#	@> $@ # truncate
#	@for file in $(CSS_MINIFIED); do cat $${file} >> $@; done
	@cat $(CSS_MINIFIED) > $@
	@echo "[tag] @import url(\"$@\");"

$(JS_TARGET): $(JS_MINIFIED)
#	@> $@ # truncate
#	@for file in $(JS_MINIFIED_DEPS); do cat $${file} >> $@; done
#	@for file in $(JS_MINIFIED); do cat $${file} >> $@; done
	@cat $(JS_MINIFIED_DEPS) > $@
	@cat $(JS_MINIFIED) >> $@
	@echo "[tag] <script type=\"text/javascript\" src=\"$@\"></script>"

clean:
	-@rm -f \
		$(CSS_MINIFIED) $(CSS_MINIFIED_EXTRA) $(CSS_TARGET) \
		$(JS_MINIFIED) $(JS_MINIFIED_EXTRA) $(JS_TARGET)
	@echo Cleaned.
