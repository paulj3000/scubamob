const gulp =require('gulp');
const babel =require('gulp-babel');
const connect = require("gulp-connect"),
      sourcemaps = require('gulp-sourcemaps'),
      webpack = require('webpack-stream'),
      javascriptObfuscator = require('gulp-javascript-obfuscator');


gulp.task('build', async () => {
   gulp.src('static/react/src/**/*.js')
      .pipe(webpack(require('./webpack.config.js')))
      .pipe(gulp.dest('static/react/dist'))
});

gulp.task('watch', async () => {
   gulp.watch(['static/react/src/**/*.js'], gulp.series(['build']));
});

gulp.task('start', gulp.series('build', 'watch'));
