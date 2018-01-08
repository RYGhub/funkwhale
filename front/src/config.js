class Config {
  constructor () {
    this.BACKEND_URL = process.env.BACKEND_URL
    if (this.BACKEND_URL === '/') {
      this.BACKEND_URL = window.location.protocol + '//' + window.location.hostname + ':' + window.location.port
    }
    if (!this.BACKEND_URL.slice(-1) === '/') {
      this.BACKEND_URL += '/'
    }
    this.API_URL = this.BACKEND_URL + 'api/v1/'
  }
}

export default new Config()
