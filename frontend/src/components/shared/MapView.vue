<template>
  <div class="map-view-wrapper" :style="{ height: typeof height === 'number' ? height + 'px' : height }">
    <iframe
      :src="iframeSrc"
      width="100%"
      height="100%"
      frameborder="0"
      allowfullscreen
      loading="lazy"
      referrerpolicy="no-referrer-when-downgrade"
      class="map-iframe"
    ></iframe>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  latitude:  { type: Number, required: true },
  longitude: { type: Number, required: true },
  height: { type: [Number, String], default: 400 },
  zoom: { type: Number, default: 16 },
});

const iframeSrc = computed(() => {
  const ll = `${props.longitude},${props.latitude}`;
  const pt = `${props.longitude},${props.latitude},pm2rdm`;
  return `https://yandex.ru/map-widget/v1/?ll=${ll}&z=${props.zoom}&pt=${pt}&l=map`;
});
</script>

<style scoped>
.map-view-wrapper {
  width: 100%;
  border-radius: 16px;
  overflow: hidden;
  border: 2px solid #FFD6BD;
}

.map-iframe {
  display: block;
  border: none;
  width: 100%;
  height: 100%;
}
</style>
