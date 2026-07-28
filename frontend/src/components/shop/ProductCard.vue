<template>
  <div class="product-card" @click="$emit('click')">
    <!-- Image wrap -->
    <div
      class="product-card__img-wrap"
      ref="wrapRef"
      @mousemove="onMouseMove"
      @mouseleave="onMouseLeave"
      @touchstart.passive="onTouchStart"
      @touchmove.passive="onTouchMove"
      @touchend.passive="onTouchEnd"
    >
      <!-- Images -->
      <div v-if="allImages.length > 0" class="product-card__slides">
        <img
          v-for="(img, idx) in allImages"
          :key="idx"
          :src="baseUrl + img"
          :alt="product.name"
          class="product-card__img"
          :class="{ active: currentIdx === idx }"
          loading="lazy"
        />
      </div>
      <div v-else class="product-card__img-placeholder">
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="1.5">
          <rect x="3" y="3" width="18" height="18" rx="2" />
          <circle cx="8.5" cy="8.5" r="1.5" />
          <polyline points="21 15 16 10 5 21" />
        </svg>
      </div>

      <!-- Progress segments (thin lines at bottom, like the design) -->
      <div v-if="allImages.length > 1" class="card-segments">
        <span
          v-for="(_, idx) in allImages"
          :key="idx"
          class="card-segment"
          :class="{ active: currentIdx === idx }"
        />
      </div>

      <!-- Favorite button -->
      <button
        class="product-card__fav"
        :class="{ active: isFavorite }"
        @click.stop="$emit('favorite')"
        :aria-label="isFavorite ? 'Убрать из избранного' : 'Добавить в избранное'"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path
            d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
            :fill="isFavorite ? 'currentColor' : 'none'"
          />
        </svg>
      </button>

      <!-- Out of stock -->
      <div v-if="product.available === 0" class="product-card__badge out-of-stock">Нет в наличии</div>
    </div>

    <!-- Info -->
    <div class="product-card__info">
      <h3 class="product-card__name">{{ product.name }}</h3>
      <span class="product-card__price">{{ formatPrice(product.price) }} ₽</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { baseUrl } from '@/stores/counter'
import { useShopStore } from '@/stores/shop'

const shopStore = useShopStore()

const props = defineProps({
  product: { type: Object, required: true },
})

defineEmits(['click', 'favorite'])

const allImages = computed(() => {
  const images = []
  if (props.product.main_image) images.push(props.product.main_image)
  if (props.product.images?.length) {
    props.product.images.forEach(img => {
      const path = img.image_path || img
      if (path && path !== props.product.main_image) images.push(path)
    })
  }
  return images
})

const isFavorite = computed(() =>
  shopStore.favoriteProductIds.includes(props.product.product_id) || !!props.product.is_favorite,
)

function formatPrice(price) {
  return Number(price).toLocaleString('ru-RU')
}

const wrapRef   = ref(null)
const currentIdx = ref(0)

function onMouseMove(e) {
  const n = allImages.value.length
  if (n < 2) return
  const rect = wrapRef.value.getBoundingClientRect()
  const x    = e.clientX - rect.left
  const idx  = Math.min(n - 1, Math.floor((x / rect.width) * n))
  currentIdx.value = idx
}

function onMouseLeave() {
  currentIdx.value = 0
}

const touchStartX = ref(0)
const touchStartIdx = ref(0)

function onTouchStart(e) {
  touchStartX.value   = e.touches[0].clientX
  touchStartIdx.value = currentIdx.value
}

function onTouchMove(e) {
  const n = allImages.value.length
  if (n < 2) return
  const rect  = wrapRef.value.getBoundingClientRect()
  const dx    = e.touches[0].clientX - touchStartX.value
  const steps = Math.round((dx / rect.width) * n)
  const idx   = Math.max(0, Math.min(n - 1, touchStartIdx.value - steps))
  currentIdx.value = idx
}

function onTouchEnd() {


}
</script>

<style scoped>
.product-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  transition: box-shadow 0.25s;
  height: 100%;
}

.product-card:hover {
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.09);
}

.product-card__img-wrap {
  position: relative;
  aspect-ratio: 3 / 4;
  overflow: hidden;
  background: #f5f3f0;
  user-select: none;
}

.product-card__slides {
  position: relative;
  width: 100%;
  height: 100%;
}

.product-card__img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0;
  transition: opacity 0.18s ease;
  pointer-events: none;
}

.product-card__img.active {
  opacity: 1;
}

.product-card__img-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-segments {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  gap: 3px;
  padding: 0 8px 8px;
  z-index: 2;
}

.card-segment {
  flex: 1;
  height: 2px;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.45);
  transition: background 0.15s;
}

.card-segment.active {
  background: rgba(255, 255, 255, 0.95);
}

.product-card__fav {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(6px);
  color: #999;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s, transform 0.2s;
  z-index: 3;
}

.product-card__fav:hover { color: #FF6C36; transform: scale(1.1); }
.product-card__fav.active { color: #FF6C36; }

.product-card__badge {
  position: absolute;
  bottom: 14px;
  left: 10px;
  padding: 3px 8px;
  border-radius: 5px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  z-index: 3;
}

.out-of-stock {
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
}

.product-card__info {
  padding: 10px 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  justify-content: space-between;
}

.product-card__name {
  font-size: 14px;
  font-weight: 500;
  color: #1a1a1a;
  margin: 0;
  line-height: 1.35;
  min-height: 2.7em;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-card__price {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a1a;
  margin-top: auto;
}
</style>
