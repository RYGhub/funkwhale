
module.exports = {
  configureWebpack: {
    resolve: {
      alias: {
        'vue$': 'vue/dist/vue.esm.js'
      }
    }
  },
  devServer: {
    disableHostCheck: true,
    proxy: {
      '^/rest': {
        target: 'http://nginx:6001',
        changeOrigin: true,
      },
      '^/staticfiles': {
        target: 'http://nginx:6001',
        changeOrigin: true,
      },
      '^/.well-known': {
        target: 'http://nginx:6001',
        changeOrigin: true,
      },
      '^/media': {
        target: 'http://nginx:6001',
        changeOrigin: true,
      },
      '^/federation': {
        target: 'http://nginx:6001',
        changeOrigin: true,
        ws: true,
      },
      '^/api': {
        target: 'http://nginx:6001',
        changeOrigin: true,
        ws: true,
      },
    }
  }
}
