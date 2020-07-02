// npm install --save-dev gulp gulp-concat gulp-rename gulp-clean-css gulp-sourcemaps gulp-uglify

const gulp = require('gulp');
const concat = require('gulp-concat');
const rename = require('gulp-rename');
const cleanCSS = require('gulp-clean-css');
const sourcemaps = require('gulp-sourcemaps');
const uglify = require('gulp-uglify');

const cssFiles = [
	'jquery-ui-1.8.6.custom/css/cupertino/jquery-ui-1.8.6.custom.css',
	'css/theme.css',
	'css/form.css',
	'css/search.css',
	'css/list.css',
	'css/pagination.css',
	'css/dashboard.css',
	'css/login.css',
	'css/tooltip.css',
	'css/modal.css',
	'css/specific-moz.css',
	'css/specific-msie.css',
	'css/specific-webkit.css',
];
const cssDest = 'css/';

const jsFiles = [
	'jquery-ui-1.8.6.custom/js/jquery-ui-1.8.6.custom.min.js',
	'js/lib/jquery.tools.min.js',
	'js/lib/jquery.simplemodal-1.4.1.js',
	'js/lib/string.format.js',
	'js/lib/date.format.js',
	'js/i18n.js',
	'js/calendar.js',
	'js/form.js',
	'js/search.js',
	'js/selection.js',
	'js/selectbox.js',
	'js/googlecharts.js',
	'js/utils.js',
];
const jsDest = 'js/';

gulp.task('styles', function() {
    return gulp.src(cssFiles)
    	.pipe(sourcemaps.init())
        .pipe(cleanCSS({compatibility: 'ie9'}))
        .pipe(sourcemaps.write())
        .pipe(concat('all.min.css'))
        .pipe(gulp.dest(cssDest));
});

gulp.task('scripts', function() {
    return gulp.src(jsFiles)
    	.pipe(sourcemaps.init())
        .pipe(uglify())
        .pipe(sourcemaps.write())
        .pipe(concat('all.min.js'))
        .pipe(gulp.dest(jsDest));
});

gulp.task('all', gulp.series('styles', 'scripts'))
