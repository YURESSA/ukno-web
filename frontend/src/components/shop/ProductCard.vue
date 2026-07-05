<template>
  <div class="product-card" @click="$emit('click')">
    <!-- Image -->
    <div class="product-card__img-wrap">
      <div 
        v-if="allImages.length > 0" 
        class="product-card__carousel"
        ref="carouselRef"
        @scroll="onScroll"
      >
        <img
          v-for="(img, idx) in allImages"
          :key="idx"
          :src="baseUrl + img"
          :alt="product.name"
          class="product-card__img"
          loading="lazy"
        />
      </div>
      <div v-else class="product-card__img-placeholder">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="1.5">
          <rect x="3" y="3" width="18" height="18" rx="2" />
          <circle cx="8.5" cy="8.5" r="1.5" />
          <polyline points="21 15 16 10 5 21" />
        </svg>
      </div>

      <!-- Carousel Dots -->
      <div v-if="allImages.length > 1" class="carousel-dots">
        <span 
          v-for="(_, idx) in allImages" 
          :key="idx" 
          class="carousel-dot"
          :class="{ active: currentImageIndex === idx }"
        ></span>
      </div>

      <!-- Carousel Arrows -->
      <button 
        v-if="allImages.length > 1"
        class="carousel-arrow carousel-arrow--prev"
        @click.stop="scrollPrev"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15 18 9 12 15 6" />
        </svg>
      </button>
      <button 
        v-if="allImages.length > 1"
        class="carousel-arrow carousel-arrow--next"
        @click.stop="scrollNext"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 18 15 12 9 6" />
        </svg>
      </button>

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

      <!-- Out of stock badge -->
      <div v-if="product.available === 0" class="product-card__badge out-of-stock">Нет в наличии</div>
    </div>

    <!-- Info -->
    <div class="product-card__info">
      {{ allImages }}
      <p v-if="product.category" class="product-card__category">{{ product.category.name }}</p>
      <h3 class="product-card__name">{{ product.name }}</h3>
      <div class="product-card__footer">
        <span class="product-card__price">{{ formatPrice(product.price) }} ₽</span>
        <span v-if="product.collection" class="product-card__collection">{{ product.collection }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { baseUrl } from '@/stores/counter';
import { useShopStore } from '@/stores/shop';

const shopStore = useShopStore();

const props = defineProps({
  product: {
    type: Object,
    required: true,
  },
})

const isFavorite = computed(() => {
  return shopStore.favoriteProductIds.includes(props.product.product_id) || !!props.product.is_favorite;
})

defineEmits(['click', 'favorite'])

function formatPrice(price) {
  return Number(price).toLocaleString('ru-RU')
}

const allImages = computed(() => {
  const images = [];
  if (props.product.main_image) {
    images.push(props.product.main_image);
  }
  if (props.product.images && props.product.images.length > 0) {
    props.product.images.forEach(img => {
      const path = img.image_path || img;
      if (path && path !== props.product.main_image) {
        images.push(path);
      }
    });
  }
  return images;
})

const carouselRef = ref(null);
const currentImageIndex = ref(0);

function onScroll() {
  if (!carouselRef.value) return;
  const scrollLeft = carouselRef.value.scrollLeft;
  const width = carouselRef.value.clientWidth;
  if (width > 0) {
    currentImageIndex.value = Math.round(scrollLeft / width);
  }
}

function scrollNext() {
  if (!carouselRef.value) return;
  const width = carouselRef.value.clientWidth;
  carouselRef.value.scrollBy({ left: width, behavior: 'smooth' });
}

function scrollPrev() {
  if (!carouselRef.value) return;
  const width = carouselRef.value.clientWidth;
  carouselRef.value.scrollBy({ left: -width, behavior: 'smooth' });
}
</script>

<style scoped>
.product-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.25s, box-shadow 0.25s;
  display: flex;
  flex-direction: column;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
}

/* Image */
.product-card__img-wrap {
  position: relative;
  aspect-ratio: 1 / 1.1;
  overflow: hidden;
  background: #f5f3f0;
}

.product-card__carousel {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
  width: 100%;
  height: 100%;
}
.product-card__carousel::-webkit-scrollbar {
  display: none;
}

.product-card__img {
  flex: 0 0 100%;
  width: 100%;
  height: 100%;
  object-fit: cover;
  scroll-snap-align: start;
}

/* Dots */
.carousel-dots {
  position: absolute;
  bottom: 12px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  gap: 6px;
  z-index: 2;
  pointer-events: none;
}

.carousel-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  transition: background 0.2s, transform 0.2s;
}

.carousel-dot.active {
  background: rgba(255, 255, 255, 1);
  transform: scale(1.2);
}

/* Arrows */
.carousel-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(4px);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s, background 0.2s;
  z-index: 2;
  color: #333;
}

@media (hover: hover) {
  .product-card__img-wrap:hover .carousel-arrow {
    opacity: 1;
  }
}

.carousel-arrow:hover {
  background: rgba(255, 255, 255, 0.95);
}

.carousel-arrow--prev {
  left: 8px;
}

.carousel-arrow--next {
  right: 8px;
}

.product-card__img-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Favorite */
.product-card__fav {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  color: #bbb;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s, background 0.2s, transform 0.2s;
}

.product-card__fav:hover {
  color: #FF6C36;
  transform: scale(1.1);
}

.product-card__fav.active {
  color: #FF6C36;
}

/* Badges */
.product-card__badge {
  position: absolute;
  bottom: 10px;
  left: 10px;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.out-of-stock {
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
}

/* Info */
.product-card__info {
  padding: 14px 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.product-card__category {
  font-size: 11px;
  font-weight: 600;
  color: #FF6C36;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.product-card__name {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 8px;
}

.product-card__price {
  font-size: 17px;
  font-weight: 700;
  color: #1a1a1a;
}

.product-card__collection {
  font-size: 11px;
  color: #999;
  font-style: italic;
}
</style>
