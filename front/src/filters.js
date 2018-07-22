import Vue from 'vue'

import moment from 'moment'
import showdown from 'showdown'

export function truncate (str, max, ellipsis) {
  max = max || 100
  ellipsis = ellipsis || '…'
  if (str.length <= max) {
    return str
  }
  return str.slice(0, max) + ellipsis
}

Vue.filter('truncate', truncate)

export function markdown (str) {
  const converter = new showdown.Converter()
  return converter.makeHtml(str)
}

Vue.filter('markdown', markdown)

export function ago (date) {
  const m = moment(date)
  return m.fromNow()
}

Vue.filter('ago', ago)

export function secondsToObject (seconds) {
  let m = moment.duration(seconds, 'seconds')
  return {
    minutes: m.minutes(),
    hours: parseInt(m.asHours())
  }
}

Vue.filter('secondsToObject', secondsToObject)

export function momentFormat (date, format) {
  format = format || 'lll'
  return moment(date).format(format)
}

Vue.filter('moment', momentFormat)

export function year (date) {
  return moment(date).year()
}

Vue.filter('year', year)

export function capitalize (str) {
  return str.charAt(0).toUpperCase() + str.slice(1)
}

Vue.filter('capitalize', capitalize)

export function humanSize (bytes) {
  let si = true
  var thresh = si ? 1000 : 1024
  if (Math.abs(bytes) < thresh) {
    return bytes + ' B'
  }
  var units = si
    ? ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    : ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
  var u = -1
  do {
    bytes /= thresh
    ++u
  } while (Math.abs(bytes) >= thresh && u < units.length - 1)
  return bytes.toFixed(1) + ' ' + units[u]
}

Vue.filter('humanSize', humanSize)

export default {}
