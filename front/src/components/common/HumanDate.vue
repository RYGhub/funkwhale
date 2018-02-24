<template>
  <time :datetime="date" :title="date | moment">{{ date | ago }}</time>
</template>
<script>
export default {
  props: ['date']
}
</script>
