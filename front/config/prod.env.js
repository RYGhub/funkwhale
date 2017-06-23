module.exports = {
  NODE_ENV: '"production"',
  BACKEND_URL: '"' + (process.env.BACKEND_URL  || '/') + '"'
}
