<template>
  <main class="main pusher" v-title="labels.title">
    <div v-if="isLoading" class="ui vertical segment">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <template v-if="object && !isLoading">
      <section class="ui head vertical stripe segment container" v-title="object.artist.name">
        <div class="ui stackable two column grid">
          <div class="column">
            <div class="ui two column grid">
              <div class="column">
                <img class="huge channel-image" v-if="object.artist.cover" :src="$store.getters['instance/absoluteUrl'](object.artist.cover.medium_square_crop)">
                <i v-else class="huge circular inverted users violet icon"></i>
              </div>
              <div class="ui column right aligned">
                <tags-list v-if="object.artist.tags && object.artist.tags.length > 0" :tags="object.artist.tags"></tags-list>
                <actor-link :avatar="false" :actor="object.attributed_to" :display-name="true"></actor-link>
                <template v-if="totalTracks > 0">
                  <div class="ui hidden very small divider"></div>
                  <translate translate-context="Content/Channel/Paragraph"
                    translate-plural="%{ count } episodes"
                    :translate-n="totalTracks"
                    :translate-params="{count: totalTracks}">
                    %{ count } episode
                  </translate>
                  <template v-if="object.attributed_to.full_username === $store.state.auth.fullUsername || $store.getters['channels/isSubscribed'](object.uuid)">
                    · <translate translate-context="Content/Channel/Paragraph" translate-plural="%{ count } subscribers" :translate-n="object.subscriptions_count" :translate-params="{count: object.subscriptions_count}">%{ count } subscriber</translate>
                  </template>
                </template>
                <div class="ui hidden small divider"></div>
                <a :href="rssUrl" target="_blank" class="ui icon small basic button">
                  <i class="feed icon"></i>
                </a>
                <div class="ui dropdown icon small basic button" ref="dropdown" v-dropdown>
                  <i class="ellipsis vertical icon"></i>
                  <div class="menu">
                    <div
                      role="button"
                      v-if="totalTracks > 0"
                      @click="showEmbedModal = !showEmbedModal"
                      class="basic item">
                      <i class="code icon"></i>
                      <translate translate-context="Content/*/Button.Label/Verb">Embed</translate>
                    </div>
                    <div class="divider"></div>
                    <div
                      role="button"
                      class="basic item"
                      v-for="obj in getReportableObjs({channel: object})"
                      :key="obj.target.type + obj.target.id"
                      @click.stop.prevent="$store.dispatch('moderation/report', obj.target)">
                      <i class="share icon" /> {{ obj.label }}
                    </div>

                    <div class="divider"></div>
                    <router-link class="basic item" v-if="$store.state.auth.availablePermissions['library']" :to="{name: 'manage.library.channels.detail', params: {id: object.uuid}}">
                      <i class="wrench icon"></i>
                      <translate translate-context="Content/Moderation/Link">Open in moderation interface</translate>
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
            <h1 class="ui header">
              <div class="left aligned content ellipsis">
                {{ object.artist.name }}
                <div class="ui hidden very small divider"></div>
                <div class="sub header">
                  {{ object.actor.full_username }}
                </div>
              </div>
            </h1>
            <div class="header-buttons">
              <div class="ui buttons">
                <play-button :is-playable="isPlayable" class="orange" :channel="object">
                  <translate translate-context="Content/Channels/Button.Label/Verb">Play</translate>
                </play-button>
              </div>
              <div class="ui buttons">
                <subscribe-button @subscribed="object.subscriptions_count += 1" @unsubscribed="object.subscriptions_count -= 1" :channel="object"></subscribe-button>
              </div>

              <modal :show.sync="showEmbedModal" v-if="totalTracks > 0">
                <div class="header">
                  <translate translate-context="Popup/Artist/Title/Verb">Embed this artist work on your website</translate>
                </div>
                <div class="content">
                  <div class="description">
                    <embed-wizard type="artist" :id="object.artist.id" />
                  </div>
                </div>
                <div class="actions">
                  <div class="ui deny button">
                    <translate translate-context="*/*/Button.Label/Verb">Cancel</translate>
                  </div>
                </div>
              </modal>
            </div>
            <div>
              <rendered-description
                @updated="object = $event"
                :content="object.artist.description"
                :update-url="`channels/${object.uuid}/`"
                :can-update="$store.state.auth.authenticated && object.attributed_to.full_username === $store.state.auth.fullUsername"></rendered-description>
            </div>
          </div>
          <div class="column">
            <div class="ui secondary pointing center aligned menu">
              <router-link class="item" :exact="true" :to="{name: 'channels.detail', params: {id: id}}">
                <translate translate-context="Content/Channels/Link">Overview</translate>
              </router-link>
              <router-link class="item" :exact="true" :to="{name: 'channels.detail.episodes', params: {id: id}}">
                <translate translate-context="Content/Channels/*">Episodes</translate>
              </router-link>
            </div>
            <div class="ui hidden divider"></div>
            <keep-alive>
              <router-view v-if="object" :object="object" @tracks-loaded="totalTracks = $event" ></router-view>
            </keep-alive>
          </div>
        </div>
      </section>
    </template>
  </main>
</template>

<script>
import axios from "axios"
import PlayButton from "@/components/audio/PlayButton"
import ChannelEntries from "@/components/audio/ChannelEntries"
import ChannelSeries from "@/components/audio/ChannelSeries"
import EmbedWizard from "@/components/audio/EmbedWizard"
import Modal from '@/components/semantic/Modal'
import TagsList from "@/components/tags/List"
import ReportMixin from '@/components/mixins/Report'

import SubscribeButton from '@/components/channels/SubscribeButton'

export default {
  mixins: [ReportMixin],
  props: ["id"],
  components: {
    PlayButton,
    EmbedWizard,
    Modal,
    TagsList,
    ChannelEntries,
    ChannelSeries,
    SubscribeButton
  },
  data() {
    return {
      isLoading: true,
      object: null,
      totalTracks: 0,
      latestTracks: null,
      showEmbedModal: false,
    }
  },
  async created() {
    await this.fetchData()
  },
  methods: {
    async fetchData() {
      var self = this
      this.isLoading = true
      let channelPromise = axios.get(`channels/${this.id}`).then(response => {
        self.object = response.data
      })
      let tracksPromise = axios.get("tracks", {params: {channel: this.id, page_size: 1, playable: true, include_channels: true}}).then(response => {
        self.totalTracks = response.data.count
      })
      await channelPromise
      await tracksPromise
      self.isLoading = false
    }
  },
  computed: {
    labels() {
      return {
        title: this.$pgettext('*/*/*', 'Channel')
      }
    },
    contentFilter () {
      let self = this
      return this.$store.getters['moderation/artistFilters']().filter((e) => {
        return e.target.id === this.object.artist.id
      })[0]
    },
    isPlayable () {
      return this.totalTracks > 0
    },
    rssUrl () {
      return this.$store.getters['instance/absoluteUrl'](`api/v1/channels/${this.id}/rss`)
    }
  },
  watch: {
    id() {
      this.fetchData()
    }
  }
}
</script>
