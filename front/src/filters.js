import Vue from 'vue'

import time from '@/utils/time'

import moment from 'moment'

export function truncate (str, max, ellipsis, middle) {
  if (max === 0) {
    return
  }
  max = max || 100
  ellipsis = ellipsis || '…'
  if (str.length <= max) {
    return str
  }
  if (middle) {
    var sepLen = 1,
        charsToShow = max - sepLen,
        frontChars = Math.ceil(charsToShow/2),
        backChars = Math.floor(charsToShow/2);

    return str.substr(0, frontChars) +
           ellipsis +
           str.substr(str.length - backChars);
  } else {
    return str.slice(0, max) + ellipsis
  }
}

Vue.filter('truncate', truncate)

export function ago (date, locale) {
  locale = locale || 'en'
  const m = moment(date)
  m.locale(locale)
  return m.calendar(null, {
    sameDay: 'LT',
    nextDay: 'L',
    nextWeek: 'L',
    lastDay: 'L',
    lastWeek: 'L',
    sameElse: 'L'
  })
}

Vue.filter('ago', ago)

export function fromNow (date, locale) {
  locale = 'en'
  moment.locale('en', {
    relativeTime: {
      future: 'in %s',
      past: '%s ago',
      s:  'seconds',
      ss: '%ss',
      m:  'a minute',
      mm: '%dm',
      h:  'an hour',
      hh: '%dh',
      d:  'a day',
      dd: '%dd',
      M:  'a month',
      MM: '%dM',
      y:  'a year',
      yy: '%dY'
    }
  });
  const m = moment(date)
  m.locale(locale)
  return m.fromNow(true)
}

Vue.filter('fromNow', fromNow)

export function secondsToObject (seconds) {
  let m = moment.duration(seconds, 'seconds')
  return {
    seconds: m.seconds(),
    minutes: m.minutes(),
    hours: m.hours()
  }
}

Vue.filter('secondsToObject', secondsToObject)

export function padDuration (duration) {
  var s = String(duration);
  while (s.length < 2) {s = "0" + s;}
  return s;
}

Vue.filter('padDuration', padDuration)

export function duration (seconds) {
  return time.parse(seconds)
}

Vue.filter('duration', duration)

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
