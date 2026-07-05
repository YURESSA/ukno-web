<template>
  <div class="shop-layout">
    <header class="shop-header">
      <div class="shop-header__inner">
        <!-- Logo -->
        <RouterLink to="/shop" class="shop-header__logo">
          <img src="/logo/mobile-logo.svg" alt="UKNO" />
          <span class="shop-header__logo-text">Мерч</span>
        </RouterLink>

        <!-- Nav -->
        <nav class="shop-header__nav">
          <RouterLink to="/shop" class="shop-nav-link" :class="{ active: isShopRoot }">
            Каталог
          </RouterLink>
          <RouterLink to="/shop/favorite" class="shop-nav-link">
            Избранное
            <span v-if="isAuthed && shopStore.favoritesCount > 0" class="shop-nav-badge">
              {{ shopStore.favoritesCount }}
            </span>
          </RouterLink>
          <RouterLink to="/shop/orders" class="shop-nav-link">
            Заказы
          </RouterLink>
        </nav>

        <!-- Actions -->
        <div class="shop-header__actions">
          <RouterLink v-if="!isAuthed" to="/login" class="shop-auth-btn">
            Войти
          </RouterLink>

          <!-- Иконка ЛК (только для авторизованных) -->
          <RouterLink v-if="isAuthed" :to="profileRoute" class="shop-icon-btn" title="Личный кабинет">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
          </RouterLink>

          <!-- Иконка корзины -->
          <RouterLink to="/shop/orders" class="shop-icon-btn" :class="{ 'has-items': cartCount > 0 }" title="Корзина / Заказы">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z" />
              <line x1="3" y1="6" x2="21" y2="6" />
              <path d="M16 10a4 4 0 0 1-8 0" />
            </svg>
            <span v-if="cartCount > 0" class="shop-cart-count">{{ cartCount }}</span>
          </RouterLink>
        </div>
      </div>
    </header>

    <main class="shop-main">
      <router-view />
    </main>

    <s-footer />
  </div>
</template>

<script setup>
import { SFooter } from '@/components/shared'
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useDataStore } from '@/stores/counter'
import { useShopStore } from '@/stores/shop'

const route = useRoute()
const dataStore = useDataStore()
const shopStore = useShopStore()

const isAuthed = computed(() => !!dataStore.auth_key)
const cartCount = computed(() => (isAuthed.value ? shopStore.cartItemsCount : 0))
const isShopRoot = computed(() => route.path === '/shop' || route.path === '/shop/')

// Ссылка на ЛК в зависимости от роли
const profileRoute = computed(() => {
  const role = dataStore.role
  if (role === 'admin') return '/admin-profile'
  if (role === 'resident') return '/resident-profile'
  return '/profile'
})

// Загружаем корзину при входе/смене авторизации
watch(
  () => dataStore.auth_key,
  async (key) => {
    if (key) {
      await shopStore.FetchCart(key)
      await shopStore.FetchFavorites(key)
    } else {
      shopStore.cart = { items: [], total_price: '0' }
      shopStore.favorites = []
    }
  },
  { immediate: true },
)
</script>

<style scoped>
.shop-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f7f6f3;
  font-family: 'Inter', sans-serif;
}

/* ── Header ── */
.shop-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: #fff;
  border-bottom: 1px solid #e8e5e0;
  box-shadow: 0 1px 12px rgba(0, 0, 0, 0.06);
}

.shop-header__inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  gap: 40px;
}

.shop-header__logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  flex-shrink: 0;
}

.shop-header__logo img {
  height: 32px;
  width: auto;
}

.shop-header__logo-text {
  font-size: 13px;
  font-weight: 600;
  color: #FF6C36;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(255, 108, 54, 0.1);
}

/* Nav */
.shop-header__nav {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.shop-nav-link {
  position: relative;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  color: #555;
  text-decoration: none;
  transition: color 0.2s, background 0.2s;
}

.shop-nav-link:hover {
  color: #1a1a1a;
  background: #f0ede8;
}

.shop-nav-link.router-link-active,
.shop-nav-link.active {
  color: #FF6C36;
  background: rgba(255, 108, 54, 0.08);
}

.shop-nav-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 9px;
  background: #FF6C36;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
}

/* Actions */
.shop-header__actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
  flex-shrink: 0;
}

.shop-auth-btn {
  padding: 7px 18px;
  border-radius: 8px;
  border: 1.5px solid #FF6C36;
  color: #FF6C36;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.2s, color 0.2s;
}

.shop-auth-btn:hover {
  background: #FF6C36;
  color: #fff;
}

.shop-icon-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 10px;
  color: #555;
  text-decoration: none;
  transition: background 0.2s, color 0.2s;
}

.shop-icon-btn:hover {
  background: #f0ede8;
  color: #1a1a1a;
}

.shop-icon-btn.has-items {
  color: #FF6C36;
}

.shop-cart-count {
  position: absolute;
  top: 4px;
  right: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 17px;
  height: 17px;
  padding: 0 4px;
  border-radius: 8.5px;
  background: #FF6C36;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  line-height: 1;
}

/* ── Main ── */
.shop-main {
  flex: 1;
  max-width: 1280px;
  width: 100%;
  margin: 0 auto;
  padding: 32px 24px;
  box-sizing: border-box;
}

/* ── Footer ── */
.shop-footer {
  border-top: 1px solid #e8e5e0;
  background: #fff;
  padding: 20px 24px;
}

.shop-footer__inner {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
  color: #888;
}

.shop-footer__inner a {
  color: #FF6C36;
  text-decoration: none;
  font-weight: 500;
}

.shop-footer__inner a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .shop-header__inner {
    gap: 16px;
    padding: 0 16px;
  }

  .shop-header__nav {
    display: none;
  }

  .shop-main {
    padding: 20px 16px;
  }
}
</style>
