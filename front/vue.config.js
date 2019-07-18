
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const webpack = require('webpack');

let plugins = [
  // do not include moment.js locales since it's quite heavy
  new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
]
if (process.env.BUNDLE_ANALYZE === '1') {
  plugins.push(new BundleAnalyzerPlugin())
}
module.exports = {
  baseUrl: process.env.BASE_URL || '/front/',
  productionSourceMap: false,
  pages: {
    embed: {
      entry: 'src/embed.js',
      template: 'public/embed.html',
      filename: 'embed.html',
    },
    index: {
      entry: 'src/main.js',
      template: 'public/index.html',
      filename: 'index.html'
    }
  },
  chainWebpack: config => {
    config.optimization.delete('splitChunks')
    config.plugins.delete('prefetch-embed')
    config.plugins.delete('prefetch-index')
  },
  configureWebpack: {
    plugins: plugins,
    devtool: false
  },
  devServer: {
    disableHostCheck: true,
    // use https://node1.funkwhale.test/front-server/ if you use docker with federation
    public: process.env.FRONT_DEVSERVER_URL || ('http://localhost:' + (process.env.VUE_PORT || '8080'))
  }
}
