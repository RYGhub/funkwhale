let url = process.env.INSTANCE_URL || '/'
module.exports = {
  NODE_ENV: '"production"',
  INSTANCE_URL: `"${url}"`
}
