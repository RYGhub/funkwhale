class Config {
  constructor () {
    this.BACKEND_URL = process.env.BACKEND_URL
    this.API_URL = this.BACKEND_URL + 'api/v1/'
  }
}

export default new Config()
