<template>
   <span :class="['volume-control', {'expanded': expanded}]" @click.prevent.stop="" @mouseover="handleOver" @mouseleave="handleLeave">
    <span
      role="button"
      v-if="sliderVolume === 0"
      :title="labels.unmute"
      :aria-label="labels.unmute"
      @click.prevent.stop="unmute">
      <i class="volume off icon"></i>
    </span>
    <span
      role="button"
      v-else-if="sliderVolume < 0.5"
      :title="labels.mute"
      :aria-label="labels.mute"
      @click.prevent.stop="mute">
      <i class="volume down icon"></i>
    </span>
    <span
      role="button"
      v-else
      :title="labels.mute"
      :aria-label="labels.mute"
      @click.prevent.stop="mute">
      <i class="volume up icon"></i>
    </span>
    <div class="popup">
      <input
        type="range"
        step="0.05"
        min="0"
        max="1"
        v-model="sliderVolume" />
    </div>
  </span>
</template>
<script>
import { mapState, mapGetters, mapActions } from "vuex"

export default {
  data () {
    return {
      expanded: false,
      timeout: null,
    }
  },
  computed: {
    sliderVolume: {
      get () {
        return this.$store.state.player.volume
      },
      set (v) {
        this.$store.commit("player/volume", v)
      }
    },
    labels () {
      return {
        unmute: this.$pgettext('Sidebar/Player/Icon.Tooltip/Verb', "Unmute"),
        mute: this.$pgettext('Sidebar/Player/Icon.Tooltip/Verb', "Mute"),

      }
    }
  },
  methods: {
    ...mapActions({
      mute: "player/mute",
      unmute: "player/unmute",
      toggleMute: "player/toggleMute",
    }),
    handleOver () {
      if (this.timeout) {
        clearTimeout(this.timeout)
      }
      this.expanded = true
    },
    handleLeave () {
      if (this.timeout) {
        clearTimeout(this.timeout)
      }
      this.timeout = setTimeout(() => {this.expanded = false}, 500)
    }
  }
}
</script>
<style lang="scss" scoped>

.volume-control {
  display: flex;
  line-height: inherit;
  align-items: center;
  position: relative;
  overflow: visible;
  input {
    max-width: 5.5em;
    height: 4px;
  }
  &.expandable {
    .popup {
      background-color: #1B1C1D;
      position: absolute;
      left: -4em;
      top: -7em;
      transform: rotate(-90deg);
      display: flex;
      align-items: center;
      height: 2.5em;
      padding: 0 0.5em;
      box-shadow: 1px 1px 3px rgba(125, 125, 125, 0.5);
    }
    input {
      max-width: 8.5em;
    }
    &:not(:hover):not(.expanded) .popup {
      display: none;
    }
  }
}
</style>
