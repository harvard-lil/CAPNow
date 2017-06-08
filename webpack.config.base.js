var path = require("path");
var webpack = require('webpack');
const autoprefixer = require('autoprefixer');
const ExtractTextPlugin = require('extract-text-webpack-plugin');

module.exports = {
  context: __dirname,
  entry: [
      './assets/js/index',
  ],
  output: {
      path: path.resolve('./assets/bundles/'),
      filename: "[name]-[hash].js",
  },

  plugins: [
    new ExtractTextPlugin('[name].css')
  ],


  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        use: [
                {
                    loader: "babel-loader",
                    options: {
                      presets: ['react', 'es2015', 'stage-0'],
                      plugins: [
                        require('babel-plugin-transform-class-properties'),  // support `onDelete = () => {` syntax so `this` works in react class methods
                      ]
                    }
                }
            ],

      },
      {
        test: /\.scss?$/,
        use: [{
                loader: "style-loader" // creates style nodes from JS strings
            }, {
                loader: "css-loader" // translates CSS into CommonJS
            }, {
                loader: "sass-loader" // compiles Sass to CSS
            }]
        }
    ]
}, // module config end

  resolve: {
    extensions: ['.js', '.jsx', '.scss'],
    modules: [
        path.join(__dirname, "./assets"),
        "node_modules"
    ]
    }
}
