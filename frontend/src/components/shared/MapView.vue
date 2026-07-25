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
  /** Широта */
  latitude:  { type: Number, required: true },
  /** Долгота */
  longitude: { type: Number, required: true },
  /** Высота блока карты */
  height: { type: [Number, String], default: 400 },
  /** Уровень приближения */
  zoom: { type: Number, default: 16 },
});

/**
 * Официальный URL виджета Яндекс Карт для iframe-встраивания.
 * yandex.ru/maps/ блокирует iframe через X-Frame-Options: SAMEORIGIN.
 * yandex.ru/map-widget/v1/ — специальный эндпоинт без этого ограничения.
 *
 * Параметры:
 *   ll  — центр карты (lon,lat)
 *   z   — zoom
 *   pt  — маркер (lon,lat,preset)  pm2rdm = красная точка
 *   l   — слой (map = схема)
 */
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
