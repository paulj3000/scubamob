const path = require('path');

const staticPath = './static/react/src'
const staticDistPath = './static/react/dist'

module.exports = {
  mode: 'development',
  entry: {
    profile: { import: `${staticPath}/profile/index.js` },
    settings: { import: `${staticPath}/settings/index.js` },
    home: { import: `${staticPath}/home/index.js` },
  },

  module: {
    rules: [
      {
        test: /\.(js)$/,
        exclude: /node_modules/,
        use: ['babel-loader']
      }
    ]
  },
  resolve: {
    extensions: ['*', '.js']
  },
  output: {
    //path: path.resolve(__dirname, './dist'),
    path: path.resolve(__dirname, staticDistPath),
    filename: '[name].js',
  },
  devServer: {
    static: path.resolve(__dirname, staticDistPath),
    //static: path.resolve(__dirname, './dist'),
  },
};
