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
    min = Math.floor(sec / 60)
    sec = sec - min * 60
    return pad(min) + ':' + pad(sec)
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
