import Vue from 'vue'

Vue.component('human-date', () => import(/* webpackChunkName: "common" */ "@/components/common/HumanDate"))
Vue.component('username', () => import(/* webpackChunkName: "common" */ "@/components/common/Username"))
Vue.component('user-link', () => import(/* webpackChunkName: "common" */ "@/components/common/UserLink"))
Vue.component('actor-link', () => import(/* webpackChunkName: "common" */ "@/components/common/ActorLink"))
Vue.component('actor-avatar', () => import(/* webpackChunkName: "common" */ "@/components/common/ActorAvatar"))
Vue.component('duration', () => import(/* webpackChunkName: "common" */ "@/components/common/Duration"))
Vue.component('dangerous-button', () => import(/* webpackChunkName: "common" */ "@/components/common/DangerousButton"))
Vue.component('message', () => import(/* webpackChunkName: "common" */ "@/components/common/Message"))
Vue.component('copy-input', () => import(/* webpackChunkName: "common" */ "@/components/common/CopyInput"))
Vue.component('ajax-button', () => import(/* webpackChunkName: "common" */ "@/components/common/AjaxButton"))
Vue.component('tooltip', () => import(/* webpackChunkName: "common" */ "@/components/common/Tooltip"))
Vue.component('empty-state', () => import(/* webpackChunkName: "common" */ "@/components/common/EmptyState"))
Vue.component('expandable-div', () => import(/* webpackChunkName: "common" */ "@/components/common/ExpandableDiv"))
Vue.component('collapse-link', () => import(/* webpackChunkName: "common" */ "@/components/common/CollapseLink"))
Vue.component('action-feedback', () => import(/* webpackChunkName: "common" */ "@/components/common/ActionFeedback"))

export default {}
