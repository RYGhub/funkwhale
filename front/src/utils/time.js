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
  }
}
