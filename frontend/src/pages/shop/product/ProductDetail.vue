<template>
  <div class="product-page">
    <!-- Loading -->
    <div v-if="shopStore.loading" class="product-skeleton-wrap">
      <div class="product-skeleton-img" />
      <div class="product-skeleton-info">
        <div class="skel skel--title" />
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
      <div class="product-detail">
        <!-- Gallery -->
        <div class="product-gallery">
          <div class="product-gallery__main">
            <img
              v-if="activeImage"
              :src="baseUrl + activeImage"
              :alt="shopStore.productDetail.name"
              class="product-gallery__img"
            />
            <div v-else class="product-gallery__placeholder">Нет фото</div>
          </div>
          <div v-if="shopStore.productDetail.images?.length > 1" class="product-gallery__thumbs">
            <button
              v-for="img in shopStore.productDetail.images"
              :key="img.image_id"
              class="product-gallery__thumb"
              :class="{ active: activeImage === img.image_path }"
              @click="activeImage = img.image_path"
            >
              <img :src="baseUrl + img.image_path" :alt="shopStore.productDetail.name" />
            </button>
          </div>
        </div>

        <!-- Info -->
        <div class="product-info">
          <p v-if="shopStore.productDetail.category" class="product-info__category">
            {{ shopStore.productDetail.category.name }}
          </p>
          <h1 class="product-info__name">{{ shopStore.productDetail.name }}</h1>
          <p class="product-info__price">{{ formatPrice(shopStore.productDetail.price) }} ₽</p>

          <!-- Colors -->
          <div v-if="shopStore.productDetail.colors?.length" class="product-option">
            <p class="product-option__label">Цвет: <strong>{{ selectedColor?.name }}</strong></p>
            <div class="color-list">
              <button
                v-for="color in shopStore.productDetail.colors"
                :key="color.color_id"
                class="color-btn"
                :class="{ active: selectedColor?.color_id === color.color_id }"
                :style="color.hex_code ? { background: color.hex_code } : {}"
                :title="color.name"
                @click="selectColor(color)"
              />
            </div>
          </div>

          <!-- Sizes -->
          <div v-if="selectedColor?.sizes?.length" class="product-option">
            <p class="product-option__label">Размер:</p>
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
                <span v-if="sizeItem.stock === 0" class="size-out"> (нет)</span>
              </button>
            </div>
          </div>

          <!-- Description -->
          <p v-if="shopStore.productDetail.description" class="product-info__desc">
            {{ shopStore.productDetail.description }}
          </p>

          <!-- Actions -->
          <div class="product-actions">
          <!-- Unified Add to Cart / Quantity Selector -->
            <div v-if="selectedVariant && selectedVariant.stock > 0" class="unified-add-btn">
              <template v-if="cartItem">
                <div class="quantity-selector unified">
                  <button class="qty-btn" @click="updateCartQty(cartItem.quantity - 1)" :disabled="isUpdatingCart">-</button>
                  <span class="qty-val">{{ cartItem.quantity }}</span>
                  <button class="qty-btn" @click="updateCartQty(cartItem.quantity + 1)" :disabled="cartItem.quantity >= selectedVariant.stock || isUpdatingCart">+</button>
                </div>
              </template>
              <template v-else>
                <button
                  class="product-add-btn"
                  :disabled="isUpdatingCart"
                  @click="addToCart"
                >
                  {{ isUpdatingCart ? 'Добавляю...' : 'В корзину' }}
                </button>
              </template>
            </div>
            <button
              v-else
              class="product-add-btn"
              disabled
            >
              Нет в наличии
            </button>

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
        </div>
      </div>

      <!-- Back -->
      <RouterLink to="/shop" class="back-link">← Обратно в каталог</RouterLink>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useShopStore } from '@/stores/shop'
import { baseUrl, useDataStore } from '@/stores/counter'

const route = useRoute()
const router = useRouter()
const shopStore = useShopStore()
const dataStore = useDataStore()

const selectedColor = ref(null)
const selectedVariant = ref(null)
const activeImage = ref(null)
const isUpdatingCart = ref(false)
const addedMessage = ref('')

const cartItem = computed(() => {
  if (!selectedVariant.value || !shopStore.cart?.items) return null;
  return shopStore.cart.items.find(item => {
    const vid = item.variant?.variant_id || item.variant_id;
    if (vid && vid === selectedVariant.value.variant_id) return true;
    return item.product?.product_id === shopStore.productDetail?.product_id && 
           item.color?.name === selectedColor.value?.name && 
           item.size?.name === selectedVariant.value?.size?.name;
  });
})

const isFavorite = computed(() => {
  return shopStore.favoriteProductIds.includes(shopStore.productDetail?.product_id) || !!shopStore.productDetail?.is_favorite;
})

onMounted(async () => {
  await shopStore.FetchProductDetail(route.params.id)
  const product = shopStore.productDetail
  if (product) {
    // Выбрать первый цвет с наличием
    const firstAvailableColor = product.colors?.find((c) => c.available > 0) || product.colors?.[0]
    if (firstAvailableColor) selectColor(firstAvailableColor)
    // Выбрать первое фото
    activeImage.value = product.images?.[0]?.image_path || product.main_image || null
  }
})

function selectColor(color) {
  selectedColor.value = color
  selectedVariant.value = color.sizes?.find((s) => s.stock > 0) || null
}

async function addToCart() {
  if (!dataStore.auth_key) {
    router.push('/login')
    return
  }
  if (!selectedVariant.value || isUpdatingCart.value) return
  isUpdatingCart.value = true
  addedMessage.value = ''
  try {
    await shopStore.AddToCart(dataStore.auth_key, selectedVariant.value.variant_id, 1)
    addedMessage.value = '✓ Добавлено в корзину'
    setTimeout(() => (addedMessage.value = ''), 2500)
  } finally {
    isUpdatingCart.value = false
  }
}

async function updateCartQty(newQty) {
  if (!dataStore.auth_key || !cartItem.value || isUpdatingCart.value) return;
  isUpdatingCart.value = true;
  try {
    if (newQty <= 0) {
      await shopStore.RemoveFromCart(dataStore.auth_key, cartItem.value.cart_item_id);
    } else {
      await shopStore.UpdateCartItem(dataStore.auth_key, cartItem.value.cart_item_id, newQty);
    }
  } finally {
    isUpdatingCart.value = false;
  }
}

async function toggleFav() {
  if (!dataStore.auth_key) {
    router.push('/login')
    return
  }
  await shopStore.ToggleFavorite(dataStore.auth_key, shopStore.productDetail.product_id)
}

function formatPrice(price) {
  return Number(price).toLocaleString('ru-RU')
}
</script>

<style scoped>
.product-page {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* ── Product layout ── */
.product-detail {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  align-items: start;
}

/* Gallery */
.product-gallery__main {
  border-radius: 16px;
  overflow: hidden;
  aspect-ratio: 1 / 1;
  background: #f5f3f0;
}

.product-gallery__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.product-gallery__img:hover {
  transform: scale(1.03);
}

.product-gallery__placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #bbb;
  font-size: 14px;
}

.product-gallery__thumbs {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.product-gallery__thumb {
  width: 72px;
  height: 72px;
  border-radius: 10px;
  overflow: hidden;
  border: 2px solid transparent;
  cursor: pointer;
  padding: 0;
  background: none;
  transition: border-color 0.2s;
}

.product-gallery__thumb.active {
  border-color: #FF6C36;
}

.product-gallery__thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Info */
.product-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.product-info__category {
  font-size: 12px;
  font-weight: 600;
  color: #FF6C36;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin: 0;
}

.product-info__name {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
  line-height: 1.2;
}

.product-info__price {
  font-size: 26px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
}

.product-info__desc {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin: 0;
}

/* Color / Size options */
.product-option {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.product-option__label {
  font-size: 13px;
  color: #555;
  margin: 0;
}

.color-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.color-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2.5px solid transparent;
  cursor: pointer;
  background: #ddd;
  transition: border-color 0.2s, transform 0.2s;
  outline-offset: 2px;
}

.color-btn:hover {
  transform: scale(1.12);
}

.color-btn.active {
  border-color: #FF6C36;
}

.size-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.size-btn {
  padding: 7px 18px;
  border-radius: 8px;
  border: 1.5px solid #e0ddd8;
  background: #fff;
  color: #333;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.size-btn:hover:not(.disabled) {
  border-color: #FF6C36;
  color: #FF6C36;
}

.size-btn.active {
  background: #FF6C36;
  border-color: #FF6C36;
  color: #fff;
}

.size-btn.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.size-out {
  font-size: 11px;
  opacity: 0.7;
}

/* Actions */
.product-actions {
  display: flex;
  gap: 12px;
  align-items: stretch;
}

.unified-add-btn {
  flex: 1;
  display: flex;
}
.unified-add-btn .product-add-btn {
  width: 100%;
}
.quantity-selector {
  display: flex;
  align-items: center;
  border: 1.5px solid #FF6C36;
  border-radius: 12px;
  background: #fff;
  overflow: hidden;
  height: 52px;
  box-sizing: border-box;
  width: 100%;
  justify-content: space-between;
}
.quantity-selector.unified .qty-btn {
  color: #FF6C36;
}
.quantity-selector.unified .qty-btn:hover:not(:disabled) {
  background: rgba(255, 108, 54, 0.1);
}

.qty-btn {
  width: 44px;
  height: 100%;
  border: none;
  background: transparent;
  font-size: 20px;
  color: #333;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.qty-btn:hover:not(:disabled) {
  background: #f0ede8;
}

.qty-btn:disabled {
  color: #bbb;
  cursor: not-allowed;
}

.qty-val {
  min-width: 32px;
  text-align: center;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.product-add-btn {
  flex: 1;
  padding: 14px 24px;
  border-radius: 12px;
  border: none;
  background: #FF6C36;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, transform 0.15s;
}

.product-add-btn:hover:not(:disabled) {
  background: #DD5827;
}

.product-add-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.product-add-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.product-fav-btn {
  width: 52px;
  height: 52px;
  border-radius: 12px;
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
.product-fav-btn.active {
  color: #FF6C36;
  border-color: #FF6C36;
}

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

/* Back */
.back-link {
  display: inline-block;
  color: #FF6C36;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: opacity 0.2s;
}

.back-link:hover {
  opacity: 0.75;
}

/* Skeleton */
.product-skeleton-wrap {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
}

.product-skeleton-img {
  aspect-ratio: 1;
  border-radius: 16px;
  background: linear-gradient(90deg, #f0ede8 25%, #e8e5e0 50%, #f0ede8 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.product-skeleton-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-top: 12px;
}

.skel {
  border-radius: 8px;
  background: linear-gradient(90deg, #f0ede8 25%, #e8e5e0 50%, #f0ede8 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skel--title { height: 36px; width: 80%; }
.skel--price { height: 32px; width: 40%; }
.skel--text  { height: 16px; width: 100%; }
.skel--text.short { width: 60%; }

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Not found */
.not-found {
  text-align: center;
  padding: 80px;
}

.not-found h2 {
  font-size: 22px;
  color: #333;
  margin-bottom: 16px;
}

.not-found a {
  color: #FF6C36;
  text-decoration: none;
  font-weight: 500;
}

@media (max-width: 768px) {
  .product-detail,
  .product-skeleton-wrap {
    grid-template-columns: 1fr;
    gap: 24px;
  }
}
</style>
