var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');

var config = require('./webpack.config.base.js');

config.entry = config.entry.concat([
  'webpack-dev-server/client?http://localhost:3000',
  'webpack/hot/only-dev-server',
]);

config.output.publicPath = 'http://localhost:3000/assets/bundles/';

config.plugins = config.plugins.concat([
  new webpack.HotModuleReplacementPlugin(),
  new webpack.NoErrorsPlugin(), // don't reload if there is an error
  new BundleTracker({filename: './webpack-stats.json'}),
]);

// pass the output from babel loader to react-hot loader
// config.module.loaders[0].loaders.unshift('react-hot');

module.exports = config;