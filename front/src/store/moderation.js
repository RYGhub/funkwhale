import axios from 'axios'
import logger from '@/logging'
import _ from '@/lodash'

export default {
  namespaced: true,
  state: {
    filters: [],
    showFilterModal: false,
    showReportModal: false,
    lastUpdate: new Date(),
    filterModalTarget: {
      type: null,
      target: null,
    },
    reportModalTarget: {
      type: null,
      target: null,
    }
  },
  mutations: {
    filterModalTarget (state, value) {
      state.filterModalTarget = value
    },
    reportModalTarget (state, value) {
      state.reportModalTarget = value
    },
    empty (state) {
      state.filters = []
    },
    lastUpdate (state, value) {
      state.lastUpdate = value
    },
    contentFilter (state, value) {
      state.filters.push(value)
    },
    showFilterModal (state, value) {
      state.showFilterModal = value
      if (!value) {
        state.filterModalTarget = {
          type: null,
          target: null,
        }
      }
    },
    showReportModal (state, value) {
      state.showReportModal = value
      if (!value) {
        state.reportModalTarget = {
          type: null,
          target: null,
        }
      }
    },
    reset (state) {
      state.filters = []
      state.filterModalTarget = null
      state.showFilterModal = false
      state.showReportModal = false
      state.reportModalTarget = {}
    },
    deleteContentFilter (state, uuid) {
      state.filters = state.filters.filter((e) => {
        return e.uuid != uuid
      })
    }
  },
  getters: {
    artistFilters: (state) => () => {
      let f = state.filters.filter((f) => {
        return f.target.type === 'artist'
      })
      let p = _.sortBy(f, [(e) => { return e.creation_date }])
      p.reverse()
      return p
    },
  },
  actions: {
    hide ({commit}, payload) {
      commit('filterModalTarget', payload)
      commit('showFilterModal', true)
    },
    report ({commit}, payload) {
      commit('reportModalTarget', payload)
      commit('showReportModal', true)
    },
    fetchContentFilters ({dispatch, state, commit, rootState}, url) {
      let params = {}
      let promise
      if (url) {
        promise = axios.get(url)
      } else {
          commit('empty')
          params = {
            page_size: 100,
            ordering: '-creation_date'
          }
          promise = axios.get('moderation/content-filters/', {params: params})
      }
      return promise.then((response) => {
        logger.default.info('Fetched a batch of ' + response.data.results.length + ' filters')
        if (response.data.next) {
          dispatch('fetchContentFilters', response.data.next)
        }
        response.data.results.forEach(result => {
          commit('contentFilter', result)
        })
      })
    },
    deleteContentFilter ({commit}, uuid) {
      return axios.delete(`moderation/content-filters/${ uuid }/`).then((response) => {
        commit('deleteContentFilter', uuid)
      })
    }
  }
}
