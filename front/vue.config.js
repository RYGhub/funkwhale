
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const webpack = require('webpack');
const PurgecssPlugin = require('purgecss-webpack-plugin')
const glob = require('glob-all')
const path = require('path')

let plugins = [
  // do not include moment.js locales since it's quite heavy
  new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
  // Remove unused CSS using purgecss. See https://github.com/FullHuman/purgecss
  // for more information about purgecss.
  new PurgecssPlugin({
    paths: glob.sync([
      path.join(__dirname, './public/index.html'),
      path.join(__dirname, './**/*.vue'),
      path.join(__dirname, './src/**/*.js')
    ])
  }),
]
if (process.env.BUNDLE_ANALYZE === '1') {
  plugins.push(new BundleAnalyzerPlugin())
}
module.exports = {
  baseUrl: '/front/',
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
  },
  configureWebpack: {
    plugins: plugins,
    resolve: {
      alias: {
        'vue$': 'vue/dist/vue.esm.js'
      }
    }
  },
  devServer: {
    disableHostCheck: true,
    // use https://node1.funkwhale.test/front-server/ if you use docker with federation
    public: process.env.FRONT_DEVSERVER_URL || ('http://localhost:' + (process.env.VUE_PORT || '8080'))
  }
}
