function pad (val) {
  val = Math.floor(val)
  if (val < 10) {
    return '0' + val
  }
  return val + ''
}

export default {
  parse: function (sec) {
    let min = 0
    let hours = Math.floor(sec/3600)
    if (hours >= 1) {
      sec = sec % 3600
    }
    min = Math.floor(sec / 60)
    sec = sec - min * 60
    if (hours >= 1) {
      return hours + ':' + pad(min) + ':' + pad(sec)
    }
    return min + ':' + pad(sec)
  },
  durationFormatted (v) {
    let duration = parseInt(v)
    if (duration % 1 !== 0) {
      return this.parse(0)
    }
    duration = Math.round(duration)
    return this.parse(duration)
  }
}
