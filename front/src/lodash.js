// cherry-pick specific lodash methods here to reduce bundle size

export default {
  clone: require('lodash/clone'),
  cloneDeep: require('lodash/cloneDeep'),
  keys: require('lodash/keys'),
  debounce: require('lodash/debounce'),
  get: require('lodash/get'),
  set: require('lodash/set'),
  merge: require('lodash/merge'),
  range: require('lodash/range'),
  shuffle: require('lodash/shuffle'),
  sortBy: require('lodash/sortBy'),
  throttle: require('lodash/throttle'),
  uniq: require('lodash/uniq'),
  remove: require('lodash/remove'),
  reverse: require('lodash/reverse'),
  isEqual: require('lodash/isEqual'),
  sum: require('lodash/sum'),
  startCase: require('lodash/startCase'),
  tap: require('lodash/tap'),
  trim: require('lodash/trim'),
}
