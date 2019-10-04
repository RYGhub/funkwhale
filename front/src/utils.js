import lodash from '@/lodash'

export function setUpdate(obj, statuses, value) {
  let updatedKeys = lodash.keys(obj)
  updatedKeys.forEach((k) => {
    statuses[k] = value
  })
}
