
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
let plugins = []
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
