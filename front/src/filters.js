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

export default {}
