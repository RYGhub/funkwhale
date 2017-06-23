import logger from '@/logging'
export default {
  get (key, d) {
    let v = localStorage.getItem(key)
    if (v === null) {
      return d
    } else {
      try {
        return JSON.parse(v).value
      } catch (e) {
        logger.default.error('Removing unparsable cached value for key ' + key)
        this.remove(key)
        return d
      }
    }
  },
  set (key, value) {
    return localStorage.setItem(key, JSON.stringify({value: value}))
  },

  remove (key) {
    return localStorage.removeItem(key)
  },

  clear () {
    localStorage.clear()
  }

}
