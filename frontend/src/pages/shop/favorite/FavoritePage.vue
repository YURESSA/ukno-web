<template>
  <div class="favorite-page">
    <!-- Not authed -->
    <div v-if="!isAuthed" class="auth-prompt">
      <div class="auth-prompt__icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#FF6C36" stroke-width="1.5">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
        </svg>
      </div>
      <h2>Нужна авторизация</h2>
      <p>Войдите, чтобы видеть избранное</p>
      <RouterLink to="/login" class="auth-prompt__btn">Войти</RouterLink>
    </div>

    <template v-else>
      <h1 class="page-title">Избранное</h1>

      <div v-if="shopStore.loading" class="loading-grid">
        <div v-for="i in 4" :key="i" class="product-skeleton" />
      </div>

      <div v-else-if="shopStore.favorites.length === 0" class="empty-state">
        <p>Вы ещё ничего не добавили в избранное</p>
        <RouterLink to="/shop" class="go-shop-btn">Перейти в каталог</RouterLink>
      </div>

      <div v-else class="products-grid">
        <ProductCard
          v-for="fav in shopStore.favorites"
          :key="fav.favorite_id"
          :product="fav.product"
          @favorite="toggleFav(fav.product)"
          @click="goToProduct(fav.product.product_id)"
        />
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDataStore } from '@/stores/counter'
import { useShopStore } from '@/stores/shop'
import ProductCard from '@/components/shop/ProductCard.vue'

const router = useRouter()
const dataStore = useDataStore()
const shopStore = useShopStore()

const isAuthed = computed(() => !!dataStore.auth_key)

onMounted(async () => {
  if (isAuthed.value) {
    await shopStore.FetchFavorites(dataStore.auth_key)
  }
})

async function toggleFav(product) {
  await shopStore.ToggleFavorite(dataStore.auth_key, product.product_id)
}

function goToProduct(productId) {
  router.push(`/shop/${productId}`)
}
</script>

<style scoped>
.favorite-page {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.page-title {
  font-size: 26px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
}

.auth-prompt {
  text-align: center;
  padding: 80px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.auth-prompt h2 {
  font-size: 22px;
  color: #1a1a1a;
  margin: 0;
}

.auth-prompt p {
  color: #888;
  margin: 0;
}

.auth-prompt__btn {
  margin-top: 8px;
  padding: 10px 28px;
  border-radius: 10px;
  background: #FF6C36;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.2s;
}

.auth-prompt__btn:hover {
  background: #DD5827;
}

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
  text-align: center;
  padding: 60px;
  color: #999;
  font-size: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.go-shop-btn {
  display: inline-block;
  padding: 10px 24px;
  border-radius: 10px;
  background: #FF6C36;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.2s;
}

.go-shop-btn:hover {
  background: #DD5827;
}

@media (max-width: 768px) {
  .products-grid,
  .loading-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
}
</style>
