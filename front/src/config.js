class Config {
  constructor () {
    this.BACKEND_URL = process.env.BACKEND_URL
    if (!this.BACKEND_URL.endsWith('/')) {
      this.BACKEND_URL += '/'
    }
    this.API_URL = this.BACKEND_URL + 'api/'
  }
}

export default new Config()
