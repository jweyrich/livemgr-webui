#
# Change these according to your needs
#

CSS_SOURCES = \
	jquery-ui-1.8.6.custom/css/cupertino/jquery-ui-1.8.6.custom.css \
	css/theme.css \
	css/form.css \
	css/search.css \
	css/list.css \
	css/pagination.css \
	css/dashboard.css \
	css/login.css \
	css/tooltip.css \
	css/modal.css

CSS_SOURCES_EXTRA = \
	css/specific-moz.css \
	css/specific-msie.css \
	css/specific-webkit.css

JS_SOURCES = \
	js/lib/jquery.simplemodal-1.4.1.js \
	js/lib/string.format.js \
	js/lib/date.format.js \
	js/i18n.js \
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
	js/lib/jquery.tools.min.js

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
	@java -jar ../lib/yuicompressor-2.4.2.jar $< -o $@

%.min.js: %.js
	@echo [js] $<
	@java -jar ../lib/yuicompressor-2.4.2.jar $< -o $@

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
