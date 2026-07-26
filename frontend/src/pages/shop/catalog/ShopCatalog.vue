<template>
  <div class="catalog-page">
    <!-- Hero Banners -->
    <section
      v-if="shopStore.banners.length > 0"
      class="hero-section"
      @touchstart="handleTouchStart"
      @touchend="handleTouchEnd"
      @mousedown="handleMouseDown"
      @mouseup="handleMouseUp"
    >
      <div class="hero-track" :style="{ transform: `translateX(-${activeBanner * 100}%)` }">
        <div
          v-for="banner in shopStore.banners"
          :key="banner.banner_id"
          class="hero-slide"
        >
          <img :src="`${baseUrl}${banner.image_path}`" class="hero-bg-img" alt="Banner background" />
          <div class="hero-content">
            <h2 v-if="banner.title" class="hero-title">{{ banner.title }}</h2>
            <p v-if="banner.description" class="hero-desc">{{ banner.description }}</p>
            <a v-if="banner.link_url" :href="banner.link_url" class="hero-cta">{{ banner.button_text || 'Смотреть коллекцию' }}</a>
            <button v-else class="hero-cta" @click="selectCategory(null)">{{ banner.button_text || 'Смотреть коллекцию' }}</button>
          </div>
        </div>
      </div>

      <!-- Стрелки -->
      <button v-if="shopStore.banners.length > 1" class="hero-arrow hero-arrow--prev" @click="prevBanner" aria-label="Предыдущий">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
          <polyline points="15 18 9 12 15 6" />
        </svg>
      </button>
      <button v-if="shopStore.banners.length > 1" class="hero-arrow hero-arrow--next" @click="nextBanner" aria-label="Следующий">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
          <polyline points="9 18 15 12 9 6" />
        </svg>
      </button>

      <!-- Точки -->
      <div v-if="shopStore.banners.length > 1" class="hero-dots">
        <button
          v-for="(_, i) in shopStore.banners"
          :key="i"
          class="hero-dot"
          :class="{ active: i === activeBanner }"
          @click="activeBanner = i"
        />
      </div>
    </section>

    <!-- Search & Filters -->
    <section class="catalog-controls">
      <!-- Search input -->
      <div class="search-box">
        <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="Поиск по названию или коллекции"
          @input="onSearchInput"
          @keyup.enter="doSearch"
        />
        <button
          v-if="searchQuery"
          class="search-clear"
          @click="clearSearch"
          aria-label="Очистить поиск"
        >✕</button>
      </div>

      <!-- Filters -->
      <div class="filters-section">
        <button class="filter-btn" :class="{ active: !selectedCategory }" @click="selectCategory(null)">Все</button>
        <button
          v-for="cat in shopStore.categories"
          :key="cat.category_id"
          class="filter-btn"
          :class="{ active: selectedCategory === cat.category_id }"
          @click="selectCategory(cat.category_id)"
        >{{ cat.name }}</button>
      </div>
    </section>

    <!-- Loading -->
    <div v-if="shopStore.loading" class="loading-grid">
      <div v-for="i in 8" :key="i" class="product-skeleton" />
    </div>

    <!-- Products grid -->
    <section v-else class="products-grid">
      <ProductCard
        v-for="product in shopStore.products"
        :key="product.product_id"
        :product="product"
        @favorite="handleFavorite(product)"
        @click="goToProduct(product.product_id)"
      />
    </section>

    <div v-if="!shopStore.loading && shopStore.products.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="1.5">
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
      </div>
      <p class="empty-title">Товары не найдены</p>
      <p v-if="searchQuery" class="empty-sub">По запросу «{{ searchQuery }}» ничего не найдено</p>
      <button v-if="searchQuery || selectedCategory" class="empty-reset" @click="resetFilters">Сбросить фильтры и поиск</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useShopStore } from '@/stores/shop'
import { useDataStore, baseUrl } from '@/stores/counter'
import ProductCard from '@/components/shop/ProductCard.vue'

const shopStore = useShopStore()
const dataStore = useDataStore()
const router = useRouter()

const selectedCategory = ref(null)
const activeBanner = ref(0)
const searchQuery = ref('')
let autoplayTimer = null
let searchDebounceTimer = null

onMounted(async () => {
  await shopStore.FetchHome()
  startAutoplay()
})

onUnmounted(() => {
  clearInterval(autoplayTimer)
  clearTimeout(searchDebounceTimer)
})

function startAutoplay() {
  if (shopStore.banners.length > 1) {
    autoplayTimer = setInterval(() => {
      activeBanner.value = (activeBanner.value + 1) % shopStore.banners.length
    }, 5000)
  }
}

function prevBanner() {
  clearInterval(autoplayTimer)
  const len = shopStore.banners.length
  activeBanner.value = (activeBanner.value - 1 + len) % len
  startAutoplay()
}

function nextBanner() {
  clearInterval(autoplayTimer)
  activeBanner.value = (activeBanner.value + 1) % shopStore.banners.length
  startAutoplay()
}

// Swipe handling for mobile & desktop
const touchStartX = ref(0)
const touchStartY = ref(0)
const isDragging = ref(false)

function handleTouchStart(e) {
  if (e.touches && e.touches.length > 0) {
    touchStartX.value = e.touches[0].clientX
    touchStartY.value = e.touches[0].clientY
    isDragging.value = true
  }
}

function handleTouchEnd(e) {
  if (!isDragging.value) return
  isDragging.value = false
  if (e.changedTouches && e.changedTouches.length > 0) {
    const deltaX = e.changedTouches[0].clientX - touchStartX.value
    const deltaY = e.changedTouches[0].clientY - touchStartY.value
    if (Math.abs(deltaX) > 40 && Math.abs(deltaX) > Math.abs(deltaY)) {
      if (deltaX < 0) {
        nextBanner()
      } else {
        prevBanner()
      }
    }
  }
}

function handleMouseDown(e) {
  touchStartX.value = e.clientX
  touchStartY.value = e.clientY
  isDragging.value = true
}

function handleMouseUp(e) {
  if (!isDragging.value) return
  isDragging.value = false
  const deltaX = e.clientX - touchStartX.value
  const deltaY = e.clientY - touchStartY.value
  if (Math.abs(deltaX) > 40 && Math.abs(deltaX) > Math.abs(deltaY)) {
    if (deltaX < 0) {
      nextBanner()
    } else {
      prevBanner()
    }
  }
}

function onSearchInput() {
  clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(() => {
    doSearch()
  }, 350)
}

async function doSearch() {
  clearTimeout(searchDebounceTimer)
  await shopStore.FetchProducts(selectedCategory.value, searchQuery.value.trim() || null)
}

async function clearSearch() {
  searchQuery.value = ''
  clearTimeout(searchDebounceTimer)
  await shopStore.FetchProducts(selectedCategory.value, null)
}

async function resetFilters() {
  selectedCategory.value = null
  searchQuery.value = ''
  clearTimeout(searchDebounceTimer)
  await shopStore.FetchProducts(null, null)
}

async function selectCategory(categoryId) {
  selectedCategory.value = categoryId
  await shopStore.FetchProducts(categoryId, searchQuery.value.trim() || null)
}

function goToProduct(productId) {
  router.push(`/shop/${productId}`)
}

async function handleFavorite(product) {
  if (!dataStore.auth_key) {
    router.push('/login')
    return
  }
  await shopStore.ToggleFavorite(dataStore.auth_key, product.product_id)
}
</script>

<style scoped>
.catalog-page {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* ── Hero Banner ── */
.hero-section {
  position: relative;
  overflow: hidden;
  height: 420px;
  margin: -32px -24px 0;
  user-select: none;
  touch-action: pan-y;
}

.hero-track {
  display: flex;
  height: 100%;
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.hero-slide {
  flex-shrink: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  position: relative;
}

.hero-bg-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center right;
  z-index: 0;
}

.hero-slide::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 1;
  background: linear-gradient(
    to right,
    rgba(15, 15, 20, 0.75) 0%,
    rgba(15, 15, 20, 0.45) 45%,
    transparent 70%
  );
}

.hero-content {
  position: relative;
  z-index: 2;
  padding: 0 70px;
  max-width: 480px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.hero-title {
  font-size: 42px;
  font-weight: 800;
  color: #fff;
  margin: 0;
  line-height: 1.1;
  text-transform: uppercase;
  letter-spacing: -0.01em;
}

.hero-desc {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.78);
  margin: 0;
  line-height: 1.55;
  max-width: 300px;
}

.hero-cta {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  padding: 11px 24px;
  border-radius: 10px;
  border: 1.5px solid rgba(255, 255, 255, 0.9);
  background: transparent;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.25s, color 0.25s;
  margin-top: 4px;
}

.hero-cta:hover {
  background: #fff;
  color: #111;
}

/* Стрелки */
.hero-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(8px);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, transform 0.2s;
}

.hero-arrow:hover {
  background: rgba(255, 255, 255, 0.28);
  transform: translateY(-50%) scale(1.08);
}

.hero-arrow--prev { left: 20px; }
.hero-arrow--next { right: 20px; }

/* Точки */
.hero-dots {
  position: absolute;
  bottom: 18px;
  left: 56px;
  display: flex;
  gap: 6px;
  z-index: 10;
}

.hero-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  padding: 0;
  transition: background 0.2s, width 0.25s, border-radius 0.25s;
}

.hero-dot.active {
  background: #fff;
  width: 22px;
  border-radius: 3px;
}

/* ── Search & Controls ── */
.catalog-controls {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  /* max-width: 520px; */
  width: calc(100% - 36px);
  background: #fcfbf9;
  border: 1.5px solid #e5e2dc;
  border-radius: 100px;
  padding: 2px 18px;
  transition: all 0.25s ease;
}

.search-box:focus-within,
.search-box:hover {
  border-color: #FF6C36;
  background: #fff;
  box-shadow: 0 4px 18px rgba(255, 108, 54, 0.08);
}

.search-icon {
  color: #888;
  flex-shrink: 0;
  margin-right: 12px;
  transition: color 0.25s ease;
}

.search-box:focus-within .search-icon {
  color: #FF6C36;
}

.search-input {
  border: none;
  background: transparent;
  width: 100%;
  font-size: 15px;
  color: #1a1a1a;
  padding: 10px 0;
  outline: none;
  font-family: inherit;
}

.search-input::placeholder {
  color: #999;
}

.search-clear {
  border: none;
  background: rgba(0, 0, 0, 0.06);
  color: #666;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  margin-left: 8px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.search-clear:hover {
  background: #FF6C36;
  color: #fff;
}

/* ── Filters ── */
.filters-section {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-btn {
  padding: 8px 20px;
  border-radius: 100px;
  border: 1.5px solid #e0ddd8;
  background: #fff;
  color: #555;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: #FF6C36;
  color: #FF6C36;
}

.filter-btn.active {
  background: #FF6C36;
  border-color: #FF6C36;
  color: #fff;
}

/* ── Products grid ── */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}

.loading-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}

.product-skeleton {
  height: 340px;
  border-radius: 16px;
  background: linear-gradient(90deg, #f0ede8 25%, #e8e5e0 50%, #f0ede8 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 70px 20px;
  background: #faf9f6;
  border-radius: 20px;
  border: 1px dashed #e0ddd8;
  gap: 12px;
}

.empty-icon {
  margin-bottom: 4px;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.empty-sub {
  font-size: 14px;
  color: #777;
  margin: 0;
}

.empty-reset {
  margin-top: 8px;
  padding: 8px 20px;
  border-radius: 100px;
  border: 1px solid #FF6C36;
  background: transparent;
  color: #FF6C36;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.empty-reset:hover {
  background: #FF6C36;
  color: #fff;
}

@media (max-width: 768px) {
  .hero-arrow {
    display: none;
  }

  .hero-section {
    height: 280px;
    margin: -20px -16px 0;
  }

  .hero-content {
    padding: 0 28px;
  }

  .hero-title {
    font-size: 26px;
  }

  .hero-desc {
    font-size: 13px;
  }

  .hero-dots {
    left: 28px;
  }

  .products-grid,
  .loading-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
}
</style>
