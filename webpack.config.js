const path = require('path');

const staticPath = './static/react/src'
const staticDistPath = './static/react/dist'

const mode = process.env.MODE || 'development'; 

if (mode == 'production') {
    console.log("** Production **");
}


module.exports = {
  mode: mode,
  entry: {
    divesite: { import: `${staticPath}/divesite/index.js` },
    profile: { import: `${staticPath}/profile/index.js` },
    settings: { import: `${staticPath}/settings/index.js` },
    home: { import: `${staticPath}/home/index.js` },
    messenger: { import: `${staticPath}/messenger/index.js` },
    chatbox: { import: `${staticPath}/chatbox/index.js` },
    collections: { import: `${staticPath}/collections/index.js` },
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
    path: path.resolve(__dirname, staticDistPath),
    filename: '[name].js',
  },
  devServer: {
    static: path.resolve(__dirname, staticDistPath),
  },
};
