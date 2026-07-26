<template>
  <div class="product-page">
    <!-- Loading -->
    <div v-if="shopStore.loading" class="product-skeleton-wrap">
      <div class="product-skeleton-img" />
      <div class="product-skeleton-info">
        <div class="skel skel--title" />
        <div class="skel skel--sub" />
        <div class="skel skel--price" />
        <div class="skel skel--text" />
        <div class="skel skel--text short" />
      </div>
    </div>

    <!-- Not found -->
    <div v-else-if="!shopStore.productDetail" class="not-found">
      <h2>Товар не найден</h2>
      <RouterLink to="/shop">← Вернуться в каталог</RouterLink>
    </div>

    <!-- Product -->
    <template v-else>
      <!-- Back -->
      <button class="back-link" @click="router.back()">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15 18 9 12 15 6" />
        </svg>
        Назад
      </button>

      <div class="product-detail">
        <!-- ── Gallery ── -->
        <div class="product-gallery">
          <div class="product-gallery__stage">
            <!-- Main image -->
            <div class="product-gallery__main" ref="stageRef">
              <div
                class="product-gallery__track"
                :style="{ transform: `translateX(-${activeIdx * 100}%)` }"
              >
                <img
                  v-for="(img, i) in allImages"
                  :key="i"
                  :src="baseUrl + img"
                  :alt="shopStore.productDetail.name"
                  class="product-gallery__slide"
                  @click="openFullscreen(i)"
                />
              </div>

              <div v-if="allImages.length === 0" class="product-gallery__placeholder">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="1.5">
                  <rect x="3" y="3" width="18" height="18" rx="2" />
                  <circle cx="8.5" cy="8.5" r="1.5" />
                  <polyline points="21 15 16 10 5 21" />
                </svg>
              </div>

              <!-- Arrows -->
              <button
                v-if="allImages.length > 1"
                class="gallery-arrow gallery-arrow--prev"
                @click="prevImage"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <polyline points="15 18 9 12 15 6" />
                </svg>
              </button>
              <button
                v-if="allImages.length > 1"
                class="gallery-arrow gallery-arrow--next"
                @click="nextImage"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </button>

              <!-- Zoom Icon -->
              <button
                v-if="allImages.length > 0"
                class="gallery-zoom-btn"
                @click="openFullscreen(activeIdx)"
                title="Открывать во весь экран"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="15 3 21 3 21 9" />
                  <polyline points="9 21 3 21 3 15" />
                  <line x1="21" y1="3" x2="10" y2="14" />
                  <line x1="3" y1="21" x2="14" y2="10" />
                </svg>
              </button>
            </div>

            <!-- Dots -->
            <div v-if="allImages.length > 1" class="gallery-dots">
              <button
                v-for="(_, i) in allImages"
                :key="i"
                class="gallery-dot"
                :class="{ active: activeIdx === i }"
                @click="activeIdx = i"
              />
            </div>

            <!-- Thumbnails -->
            <div v-if="allImages.length > 1" class="product-gallery__thumbs">
              <button
                v-for="(img, i) in allImages"
                :key="i"
                class="product-gallery__thumb"
                :class="{ active: activeIdx === i }"
                @click="activeIdx = i"
              >
                <img :src="baseUrl + img" :alt="shopStore.productDetail.name" />
              </button>
            </div>
          </div>
        </div>

        <!-- ── Info ── -->
        <div class="product-info">
          <!-- Title -->
          <h1 class="product-info__name">{{ shopStore.productDetail.name }}</h1>

          <!-- Collection -->
          <p v-if="shopStore.productDetail.collection" class="product-info__collection">
            Коллекция: {{ shopStore.productDetail.collection }}
          </p>

          <!-- Colors -->
          <div v-if="shopStore.productDetail.colors?.length" class="product-option">
            <p class="product-option__label">Цвет</p>
            <div class="color-list">
              <button
                v-for="color in shopStore.productDetail.colors"
                :key="color.color_id"
                class="color-btn"
                :class="{ active: selectedColor?.color_id === color.color_id }"
                :style="color.hex_code ? { background: color.hex_code } : { background: '#e0ddd8' }"
                :title="color.name"
                @click="selectColor(color)"
              >
                <svg
                  v-if="selectedColor?.color_id === color.color_id"
                  class="color-check"
                  width="14" height="14" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" stroke-width="3"
                >
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Sizes -->
          <div v-if="selectedColor?.sizes?.length" class="product-option">
            <p class="product-option__label">Размер</p>
            <div class="size-list">
              <button
                v-for="sizeItem in selectedColor.sizes"
                :key="sizeItem.variant_id"
                class="size-btn"
                :class="{
                  active: selectedVariant?.variant_id === sizeItem.variant_id,
                  disabled: sizeItem.stock === 0,
                }"
                :disabled="sizeItem.stock === 0"
                @click="selectedVariant = sizeItem"
              >
                {{ sizeItem.size?.name }}
              </button>
            </div>
            <button class="size-chart-link" @click="showSizeChart = true">
              Таблица размеров
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="6 9 12 15 18 9" />
              </svg>
            </button>
          </div>

          <!-- Size Chart Modal -->
          <Teleport to="body">
            <Transition name="modal">
              <div v-if="showSizeChart" class="size-modal-overlay" @click.self="showSizeChart = false">
                <div class="size-modal">
                  <div class="size-modal__header">
                    <span class="size-modal__title">ТАБЛИЦА РАЗМЕРОВ</span>
                    <button class="size-modal__close" @click="showSizeChart = false">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <line x1="18" y1="6" x2="6" y2="18" />
                        <line x1="6" y1="6" x2="18" y2="18" />
                      </svg>
                    </button>
                  </div>
                  <div class="size-modal__body">
                    <table class="size-table">
                      <thead>
                        <tr>
                          <th>Российский размер</th>
                          <th>Размер производителя</th>
                          <th>Обхват груди, в см</th>
                          <th>Обхват бедер, в см</th>
                          <th>Обхват талии, в см</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="row in sizeChart" :key="row.ru">
                          <td>{{ row.ru }}</td>
                          <td>{{ row.intl }}</td>
                          <td>{{ row.chest }}</td>
                          <td>{{ row.hips }}</td>
                          <td>{{ row.waist }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </Transition>
          </Teleport>

          <!-- ── Fullscreen Gallery Modal ── -->
          <Teleport to="body">
            <Transition name="fade">
              <div
                v-if="showFullscreen"
                class="fullscreen-gallery-modal"
                @click.self="closeFullscreen"
                @touchstart="handleFsTouchStart"
                @touchend="handleFsTouchEnd"
                @mousedown="handleFsMouseDown"
                @mouseup="handleFsMouseUp"
              >
                <!-- Close button -->
                <button class="fullscreen-close" @click="closeFullscreen" aria-label="Закрыть">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                </button>

                <!-- Counter -->
                <div class="fullscreen-counter">
                  {{ fullscreenIdx + 1 }} / {{ allImages.length }}
                </div>

                <!-- Arrows -->
                <button
                  v-if="allImages.length > 1"
                  class="fullscreen-arrow fullscreen-arrow--prev"
                  @click.stop="prevFullscreenImage"
                  aria-label="Предыдущее фото"
                >
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <polyline points="15 18 9 12 15 6" />
                  </svg>
                </button>

                <button
                  v-if="allImages.length > 1"
                  class="fullscreen-arrow fullscreen-arrow--next"
                  @click.stop="nextFullscreenImage"
                  aria-label="Следующее фото"
                >
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <polyline points="9 18 15 12 9 6" />
                  </svg>
                </button>

                <!-- Main Fullscreen Slide -->
                <div class="fullscreen-image-wrap" @click.self="closeFullscreen">
                  <img
                    :src="baseUrl + allImages[fullscreenIdx]"
                    :alt="shopStore.productDetail.name"
                    class="fullscreen-image"
                  />
                </div>

                <!-- Bottom Thumbnails -->
                <div v-if="allImages.length > 1" class="fullscreen-thumbs" @click.stop>
                  <button
                    v-for="(img, i) in allImages"
                    :key="i"
                    class="fullscreen-thumb"
                    :class="{ active: fullscreenIdx === i }"
                    @click="fullscreenIdx = i"
                  >
                    <img :src="baseUrl + img" :alt="shopStore.productDetail.name" />
                  </button>
                </div>
              </div>
            </Transition>
          </Teleport>

          <!-- Price -->
          <p class="product-info__price">{{ formatPrice(shopStore.productDetail.price) }} ₽</p>

          <!-- Actions -->
          <div class="product-actions">
            <!-- Add / Qty -->
            <div v-if="selectedVariant && selectedVariant.stock > 0" class="unified-add-btn">
              <template v-if="cartItem">
                <div class="quantity-selector">
                  <button class="qty-btn" @click="updateCartQty(cartItem.quantity - 1)" :disabled="isUpdatingCart">−</button>
                  <span class="qty-val">{{ cartItem.quantity }}</span>
                  <button class="qty-btn" @click="updateCartQty(cartItem.quantity + 1)" :disabled="cartItem.quantity >= selectedVariant.stock || isUpdatingCart">+</button>
                </div>
              </template>
              <template v-else>
                <button class="product-add-btn" :disabled="isUpdatingCart" @click="addToCart">
                  {{ isUpdatingCart ? 'Добавляю...' : 'Купить' }}
                </button>
              </template>
            </div>
            <button v-else class="product-add-btn" disabled>
              {{ selectedVariant ? 'Нет в наличии' : 'Выберите размер' }}
            </button>

            <!-- Favorite -->
            <button
              class="product-fav-btn"
              :class="{ active: isFavorite }"
              @click="toggleFav"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path
                  d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
                  :fill="isFavorite ? 'currentColor' : 'none'"
                />
              </svg>
            </button>
          </div>

          <p v-if="addedMessage" class="added-message">{{ addedMessage }}</p>

          <!-- Description -->
          <p v-if="shopStore.productDetail.description" class="product-info__desc">
            <h4>Описание</h4>
            {{ shopStore.productDetail.description }}
          </p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useShopStore } from '@/stores/shop'
import { baseUrl, useDataStore } from '@/stores/counter'

const route = useRoute()
const router = useRouter()
const shopStore = useShopStore()
const dataStore = useDataStore()

const selectedColor   = ref(null)
const selectedVariant = ref(null)
const activeIdx       = ref(0)
const isUpdatingCart  = ref(false)
const addedMessage    = ref('')
const showSizeChart   = ref(false)

const sizeChart = [
  { ru: 42, intl: 'XS',  chest: '82-90',   hips: '90-98',   waist: '62-70' },
  { ru: 44, intl: 'S',   chest: '86-94',   hips: '94-102',  waist: '66-74' },
  { ru: 46, intl: 'M',   chest: '90-98',   hips: '98-104',  waist: '70-78' },
  { ru: 48, intl: 'L',   chest: '94-102',  hips: '102-110', waist: '74-82' },
  { ru: 50, intl: 'XL',  chest: '98-106',  hips: '106-114', waist: '78-86' },
  { ru: 52, intl: 'XXL', chest: '102-110', hips: '110-118', waist: '82-92' },
  { ru: 54, intl: '3XL', chest: '110-118', hips: '116-124', waist: '98-106' },
  { ru: 56, intl: '4XL', chest: '118-126', hips: '126-134', waist: '98-106' },
]

// All images for the gallery
const allImages = computed(() => {
  const p = shopStore.productDetail
  if (!p) return []
  const imgs = []
  if (p.main_image) imgs.push(p.main_image)
  if (p.images?.length) {
    p.images.forEach(img => {
      const path = img.image_path || img
      if (path && path !== p.main_image) imgs.push(path)
    })
  }
  return imgs
})

const cartItem = computed(() => {
  if (!selectedVariant.value || !shopStore.cart?.items) return null
  return shopStore.cart.items.find(item => {
    const vid = item.variant?.variant_id || item.variant_id
    if (vid && vid === selectedVariant.value.variant_id) return true
    return (
      item.product?.product_id === shopStore.productDetail?.product_id &&
      item.color?.name === selectedColor.value?.name &&
      item.size?.name === selectedVariant.value?.size?.name
    )
  })
})

const isFavorite = computed(() =>
  shopStore.favoriteProductIds.includes(shopStore.productDetail?.product_id) ||
  !!shopStore.productDetail?.is_favorite,
)

onMounted(async () => {
  window.addEventListener('keydown', handleKeyDown)
  await shopStore.FetchProductDetail(route.params.id)
  const p = shopStore.productDetail
  if (p) {
    const firstColor = p.colors?.find(c => c.available > 0) || p.colors?.[0]
    if (firstColor) selectColor(firstColor)
    activeIdx.value = 0
  }
})

function selectColor(color) {
  selectedColor.value  = color
  selectedVariant.value = color.sizes?.find(s => s.stock > 0) || null
}

function prevImage() {
  activeIdx.value = (activeIdx.value - 1 + allImages.value.length) % allImages.value.length
}
function nextImage() {
  activeIdx.value = (activeIdx.value + 1) % allImages.value.length
}

async function addToCart() {
  if (!dataStore.auth_key) { router.push('/login'); return }
  if (!selectedVariant.value || isUpdatingCart.value) return
  isUpdatingCart.value = true
  addedMessage.value   = ''
  try {
    await shopStore.AddToCart(dataStore.auth_key, selectedVariant.value.variant_id, 1)
    addedMessage.value = '✓ Добавлено в корзину'
    setTimeout(() => (addedMessage.value = ''), 2500)
  } finally {
    isUpdatingCart.value = false
  }
}

async function updateCartQty(newQty) {
  if (!dataStore.auth_key || !cartItem.value || isUpdatingCart.value) return
  isUpdatingCart.value = true
  try {
    if (newQty <= 0) await shopStore.RemoveFromCart(dataStore.auth_key, cartItem.value.cart_item_id)
    else             await shopStore.UpdateCartItem(dataStore.auth_key, cartItem.value.cart_item_id, newQty)
  } finally {
    isUpdatingCart.value = false
  }
}

async function toggleFav() {
  if (!dataStore.auth_key) { router.push('/login'); return }
  await shopStore.ToggleFavorite(dataStore.auth_key, shopStore.productDetail.product_id)
}

function formatPrice(price) {
  return Number(price).toLocaleString('ru-RU')
}

// ── Fullscreen Gallery Modal ──
const showFullscreen = ref(false)
const fullscreenIdx  = ref(0)

function openFullscreen(idx) {
  fullscreenIdx.value = idx
  showFullscreen.value = true
}

function closeFullscreen() {
  showFullscreen.value = false
}

function prevFullscreenImage() {
  const len = allImages.value.length
  if (len === 0) return
  fullscreenIdx.value = (fullscreenIdx.value - 1 + len) % len
}

function nextFullscreenImage() {
  const len = allImages.value.length
  if (len === 0) return
  fullscreenIdx.value = (fullscreenIdx.value + 1) % len
}

// Swipe support for fullscreen modal
const fsTouchStartX = ref(0)
const fsTouchStartY = ref(0)
const fsDragging    = ref(false)

function handleFsTouchStart(e) {
  if (e.touches && e.touches.length > 0) {
    fsTouchStartX.value = e.touches[0].clientX
    fsTouchStartY.value = e.touches[0].clientY
    fsDragging.value = true
  }
}

function handleFsTouchEnd(e) {
  if (!fsDragging.value) return
  fsDragging.value = false
  if (e.changedTouches && e.changedTouches.length > 0) {
    const deltaX = e.changedTouches[0].clientX - fsTouchStartX.value
    const deltaY = e.changedTouches[0].clientY - fsTouchStartY.value
    if (Math.abs(deltaX) > 40 && Math.abs(deltaX) > Math.abs(deltaY)) {
      if (deltaX < 0) {
        nextFullscreenImage()
      } else {
        prevFullscreenImage()
      }
    }
  }
}

function handleFsMouseDown(e) {
  fsTouchStartX.value = e.clientX
  fsTouchStartY.value = e.clientY
  fsDragging.value = true
}

function handleFsMouseUp(e) {
  if (!fsDragging.value) return
  fsDragging.value = false
  const deltaX = e.clientX - fsTouchStartX.value
  const deltaY = e.clientY - fsTouchStartY.value
  if (Math.abs(deltaX) > 40 && Math.abs(deltaX) > Math.abs(deltaY)) {
    if (deltaX < 0) {
      nextFullscreenImage()
    } else {
      prevFullscreenImage()
    }
  }
}

function handleKeyDown(e) {
  if (!showFullscreen.value) return
  if (e.key === 'Escape') closeFullscreen()
  else if (e.key === 'ArrowLeft') prevFullscreenImage()
  else if (e.key === 'ArrowRight') nextFullscreenImage()
}

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
.product-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ── Back ── */
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #555;
  font-size: 14px;
  font-weight: 500;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s;
}
.back-link:hover { color: #FF6C36; }

/* ── Layout ── */
.product-detail {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  align-items: start;
}

/* ── Gallery ── */
.product-gallery__stage {
  position: relative;
}

.product-gallery__main {
  border-radius: 12px;
  overflow: hidden;
  aspect-ratio: 3 / 4;
  background: #f5f3f0;
  position: relative;
}

.product-gallery__track {
  display: flex;
  height: 100%;
  transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.product-gallery__slide {
  flex: 0 0 100%;
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: zoom-in;
}

.gallery-zoom-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 38px;
  height: 38px;
  border-radius: 8px;
  border: none;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(6px);
  color: #333;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, transform 0.15s;
  z-index: 2;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.gallery-zoom-btn:hover {
  background: #fff;
  transform: scale(1.06);
}

.product-gallery__placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Arrows */
.gallery-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(4px);
  color: #333;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, transform 0.15s;
  z-index: 2;
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);
}
.gallery-arrow:hover { background: #fff; transform: translateY(-50%) scale(1.08); }
.gallery-arrow--prev { left: 10px; }
.gallery-arrow--next { right: 10px; }

/* Dots */
.gallery-dots {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin-top: 10px;
}
.gallery-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  border: none;
  background: #d0cdc8;
  cursor: pointer;
  padding: 0;
  transition: background 0.2s, transform 0.2s;
}
.gallery-dot.active { background: #FF6C36; transform: scale(1.25); }

/* Thumbnails */
.product-gallery__thumbs {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}
.product-gallery__thumb {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid transparent;
  cursor: pointer;
  padding: 0;
  background: none;
  transition: border-color 0.2s;
}
.product-gallery__thumb.active { border-color: #FF6C36; }
.product-gallery__thumb img { width: 100%; height: 100%; object-fit: cover; }

/* ── Info ── */
.product-info {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.product-info__name {
  font-size: 24px;
  font-weight: 900;
  color: #1a1a1a;
  margin: 0;
  line-height: 1.2;
  text-transform: uppercase;
  letter-spacing: 0.01em;
}

.product-info__collection {
  font-size: 13px;
  color: #888;
  margin: 0;
}

.product-info__price {
  font-size: 28px;
  font-weight: 800;
  color: #1a1a1a;
  margin: 0;
  letter-spacing: -0.01em;
}

.product-info__desc {
  font-size: 14px;
  color: #555;
  line-height: 1.7;
  margin: 0;
  padding-top: 4px;
  border-top: 1px solid #e8e5e0;
  white-space: pre-line;
}

/* ── Options ── */
.product-option {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.product-option__label {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

/* Colors */
.color-list { display: flex; gap: 8px; flex-wrap: wrap; }

.color-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 2px solid transparent;
  cursor: pointer;
  background: #ddd;
  transition: border-color 0.2s, transform 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.color-btn:hover { transform: scale(1.08); }
.color-btn.active { border-color: #333; }
.color-check { color: #fff; filter: drop-shadow(0 0 1px rgba(0,0,0,0.4)); }

/* Sizes */
.size-list { display: flex; gap: 8px; flex-wrap: wrap; }

.size-btn {
  min-width: 44px;
  height: 40px;
  padding: 0 14px;
  border-radius: 8px;
  border: 1.5px solid #e0ddd8;
  background: #fff;
  color: #333;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}
.size-btn:hover:not(.disabled):not(.active) { border-color: #FF6C36; color: #FF6C36; }
.size-btn.active { background: #FF6C36; border-color: #FF6C36; color: #fff; font-weight: 700; }
.size-btn.active:hover { color: #fff; }
.size-btn.disabled { opacity: 0.35; cursor: not-allowed; }

/* ── Actions ── */
.product-actions {
  display: flex;
  gap: 10px;
  align-items: stretch;
}

.unified-add-btn { flex: 1; display: flex; }
.unified-add-btn .product-add-btn { width: 100%; }

.product-add-btn {
  flex: 1;
  padding: 14px 24px;
  border-radius: 10px;
  border: none;
  background: #FF6C36;
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s, transform 0.15s;
  letter-spacing: 0.01em;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}
.product-add-btn:hover:not(:disabled) { background: #DD5827; }
.product-add-btn:active:not(:disabled) { transform: scale(0.98); }
.product-add-btn:disabled { background: #ccc; cursor: not-allowed; }

.product-fav-btn {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  border: 1.5px solid #e0ddd8;
  background: #fff;
  color: #bbb;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s, border-color 0.2s;
  flex-shrink: 0;
}
.product-fav-btn:hover,
.product-fav-btn.active { color: #FF6C36; border-color: #FF6C36; }

/* Quantity selector */
.quantity-selector {
  display: flex;
  align-items: center;
  border: 1.5px solid #FF6C36;
  border-radius: 10px;
  background: #fff;
  overflow: hidden;
  height: 50px;
  width: 100%;
  justify-content: space-between;
  box-sizing: border-box;
}
.qty-btn {
  width: 44px; height: 100%;
  border: none; background: transparent;
  font-size: 22px; color: #FF6C36;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.15s;
}
.qty-btn:hover:not(:disabled) { background: rgba(255,108,54,0.08); }
.qty-btn:disabled { color: #ddd; cursor: not-allowed; }
.qty-val {
  min-width: 32px; text-align: center;
  font-size: 16px; font-weight: 700; color: #1a1a1a;
}

/* Messages */
.added-message {
  font-size: 14px;
  color: #22c55e;
  font-weight: 500;
  margin: 0;
  animation: fadeIn 0.3s ease;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── Skeleton ── */
.product-skeleton-wrap {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
}
.product-skeleton-img {
  aspect-ratio: 3 / 4;
  border-radius: 12px;
  background: linear-gradient(90deg, #f0ede8 25%, #e8e5e0 50%, #f0ede8 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
.product-skeleton-info { display: flex; flex-direction: column; gap: 16px; padding-top: 12px; }
.skel {
  border-radius: 8px;
  background: linear-gradient(90deg, #f0ede8 25%, #e8e5e0 50%, #f0ede8 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
.skel--title { height: 36px; width: 85%; }
.skel--sub   { height: 16px; width: 50%; }
.skel--price { height: 32px; width: 35%; }
.skel--text  { height: 14px; width: 100%; }
.skel--text.short { width: 65%; }
@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ── Size chart link ── */
.size-chart-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  padding: 0;
  font-size: 13px;
  font-weight: 500;
  color: #FF6C36;
  cursor: pointer;
  transition: opacity 0.2s;
  margin-top: 2px;
}
.size-chart-link:hover { opacity: 0.75; }

/* ── Size modal ── */
.size-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 16px;
  backdrop-filter: blur(2px);
}

.size-modal {
  background: #fff;
  border-radius: 14px;
  width: 100%;
  max-width: 640px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.size-modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 16px;
  border-bottom: 1px solid #e8e5e0;
}

.size-modal__title {
  font-size: 16px;
  font-weight: 800;
  color: #1a1a1a;
  letter-spacing: 0.03em;
}

.size-modal__close {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: #f5f3f0;
  color: #555;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, color 0.2s;
}
.size-modal__close:hover { background: #e8e5e0; color: #1a1a1a; }

.size-modal__body {
  overflow-y: auto;
  padding: 0 24px 24px;
}

.size-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
}

.size-table th,
.size-table td {
  padding: 12px 10px;
  text-align: center;
  font-size: 13px;
  color: #333;
  border-bottom: 1px solid #f0ede8;
}

.size-table th {
  font-size: 12px;
  font-weight: 600;
  color: #888;
  padding-top: 16px;
}

.size-table tbody tr:hover td { background: #fafaf8; }
.size-table tbody tr:last-child td { border-bottom: none; }

/* Modal transition */
.modal-enter-active,
.modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-active .size-modal,
.modal-leave-active .size-modal { transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1); }
.modal-enter-from,
.modal-leave-to { opacity: 0; }
.modal-enter-from .size-modal { transform: scale(0.94) translateY(12px); }
.modal-leave-to .size-modal   { transform: scale(0.96) translateY(8px); }

/* ── Not found ── */
.not-found { text-align: center; padding: 80px; }
.not-found h2 { font-size: 22px; color: #333; margin-bottom: 16px; }
.not-found a { color: #FF6C36; text-decoration: none; font-weight: 500; }

/* ── Responsive ── */
@media (max-width: 768px) {
  .product-detail,
  .product-skeleton-wrap {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .product-gallery__main {
    aspect-ratio: 1 / 1;
    border-radius: 10px;
  }

  .product-info { gap: 14px; }
  .product-info__name { font-size: 18px; }
  .product-info__price { font-size: 22px; }

  .product-actions {
    position: sticky;
    bottom: 0;
    left: 0; right: 0;
    background: #fff;
    padding: 12px 0 8px;
    box-shadow: 0 -4px 16px rgba(0,0,0,0.08);
    z-index: 10;
    margin: 0 -16px;
    padding: 12px 16px env(safe-area-inset-bottom, 8px);
  }

  .product-add-btn {
    font-size: 15px;
    padding: 13px 16px;
  }

  .size-btn {
    min-width: 40px;
    height: 38px;
    font-size: 13px;
    padding: 0 12px;
  }

  /* Modal slides up from bottom on mobile */
  .size-modal-overlay {
    align-items: flex-end;
    padding: 0;
  }
  .size-modal {
    border-radius: 16px 16px 0 0;
    max-height: 85vh;
    max-width: 100%;
  }
  .modal-enter-from .size-modal,
  .modal-leave-to .size-modal {
    transform: translateY(100%);
  }

  .size-table th,
  .size-table td {
    padding: 10px 6px;
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .product-info__name { font-size: 16px; }
  .gallery-arrow { width: 30px; height: 30px; }
}

/* ── Fullscreen Gallery Modal ── */
.fullscreen-gallery-modal {
  position: fixed;
  inset: 0;
  z-index: 10000;
  background: rgba(10, 10, 14, 0.94);
  backdrop-filter: blur(14px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  user-select: none;
  touch-action: pan-y;
}

.fullscreen-close {
  position: absolute;
  top: 24px;
  right: 28px;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, transform 0.2s;
  z-index: 10;
}
.fullscreen-close:hover {
  background: rgba(255, 255, 255, 0.28);
  transform: scale(1.08);
}

.fullscreen-counter {
  position: absolute;
  top: 28px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  background: rgba(0, 0, 0, 0.45);
  padding: 6px 16px;
  border-radius: 20px;
  z-index: 10;
  letter-spacing: 0.05em;
}

.fullscreen-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, transform 0.2s;
  z-index: 10;
}
.fullscreen-arrow:hover {
  background: rgba(255, 255, 255, 0.32);
  transform: translateY(-50%) scale(1.08);
}
.fullscreen-arrow--prev { left: 24px; }
.fullscreen-arrow--next { right: 24px; }

.fullscreen-image-wrap {
  width: 100%;
  height: 75vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 80px;
  box-sizing: border-box;
}

.fullscreen-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fullscreen-thumbs {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
  max-width: 90vw;
  overflow-x: auto;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  backdrop-filter: blur(8px);
  z-index: 10;
}

.fullscreen-thumb {
  width: 54px;
  height: 54px;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid transparent;
  cursor: pointer;
  padding: 0;
  background: #222;
  flex-shrink: 0;
  opacity: 0.6;
  transition: all 0.2s;
}
.fullscreen-thumb.active {
  border-color: #FF6C36;
  opacity: 1;
  transform: translateY(-2px);
}
.fullscreen-thumb:hover {
  opacity: 0.9;
}
.fullscreen-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

@media (max-width: 768px) {
  .fullscreen-image-wrap {
    padding: 0 16px;
    height: 70vh;
  }
  .fullscreen-arrow {
    width: 44px;
    height: 44px;
  }
  .fullscreen-arrow--prev { left: 10px; }
  .fullscreen-arrow--next { right: 10px; }
  .fullscreen-close {
    top: 16px;
    right: 16px;
    width: 40px;
    height: 40px;
  }
  .fullscreen-counter {
    top: 20px;
  }
}
</style>
