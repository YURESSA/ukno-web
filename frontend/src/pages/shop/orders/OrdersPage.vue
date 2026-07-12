<template>
  <div class="orders-page">
    <!-- Not authed -->
    <div v-if="!isAuthed" class="auth-prompt">
      <div class="auth-prompt__icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#FF6C36" stroke-width="1.5">
          <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z" />
          <line x1="3" y1="6" x2="21" y2="6" />
          <path d="M16 10a4 4 0 0 1-8 0" />
        </svg>
      </div>
      <h2>Нужна авторизация</h2>
      <p>Войдите, чтобы управлять корзиной</p>
      <RouterLink to="/login" class="auth-prompt__btn">Войти</RouterLink>
    </div>

    <template v-else>
      <!-- Tabs -->
      <div class="orders-tabs">
        <button
          class="orders-tab"
          :class="{ active: activeTab === 'cart' || activeTab === 'checkout' }"
          @click="activeTab = 'cart'"
        >
          Корзина
          <span v-if="shopStore.cartItemsCount > 0" class="tab-badge">{{ shopStore.cartItemsCount }}</span>
        </button>
        <button
          class="orders-tab"
          :class="{ active: activeTab === 'orders' }"
          @click="loadOrders"
        >
          Мои заказы
        </button>
      </div>

      <!-- ─── CART ─────────────────────────────────────────────────────────── -->
      <div v-if="activeTab === 'cart'">
        <div v-if="shopStore.cartLoading" class="cart-loading">Загружаем корзину...</div>

        <div v-else-if="shopStore.cart.items.length === 0" class="empty-cart">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="1.5">
            <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z" />
            <line x1="3" y1="6" x2="21" y2="6" />
            <path d="M16 10a4 4 0 0 1-8 0" />
          </svg>
          <p>Корзина пуста</p>
          <RouterLink to="/shop" class="go-shop-btn">Перейти в каталог</RouterLink>
        </div>

        <template v-else>
          <h1 class="page-title">КОРЗИНА</h1>
          <div class="cart-divider" />

          <div class="cart-layout">
            <!-- Items -->
            <div class="cart-items">
              <div
                v-for="item in shopStore.cart.items"
                :key="item.cart_item_id"
                class="cart-item"
              >
                <!-- Image -->
                <div class="cart-item__img-wrap">
                  <img
                    v-if="item.product?.main_image"
                    :src="baseUrl + item.product.main_image"
                    :alt="item.product?.name"
                    class="cart-item__img"
                  />
                  <div v-else class="cart-item__img-placeholder" />
                </div>

                <!-- Info -->
                <div class="cart-item__body">
                  <div class="cart-item__header">
                    <RouterLink :to="`/shop/${item.product?.product_id}`" class="cart-item__name">
                      {{ item.product?.name }}
                    </RouterLink>
                    <div class="cart-item__actions">
                      <button
                        class="cart-item__action-btn"
                        :class="{ fav: isFavorite(item.product?.product_id) }"
                        @click="toggleFav(item.product)"
                        title="В избранное"
                      >
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                          <path
                            d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
                            :fill="isFavorite(item.product?.product_id) ? 'currentColor' : 'none'"
                          />
                        </svg>
                      </button>
                      <button class="cart-item__action-btn delete" @click="removeItem(item)" title="Удалить">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                          <polyline points="3 6 5 6 21 6" />
                          <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
                          <path d="M10 11v6M14 11v6" />
                          <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2" />
                        </svg>
                      </button>
                    </div>
                  </div>

                  <div class="cart-item__meta">
                    <span v-if="item.color">{{ item.color.name }}</span>
                    <span v-if="item.size">{{ item.size.name }}</span>
                  </div>

                  <!-- Qty -->
                  <div class="cart-item__qty">
                    <button class="qty-btn" @click="updateQty(item, item.quantity - 1)" :disabled="item.quantity <= 1">-</button>
                    <span class="qty-val">{{ item.quantity }}</span>
                    <button class="qty-btn" @click="updateQty(item, item.quantity + 1)" :disabled="item.quantity >= item.available">+</button>
                  </div>

                  <div class="cart-item__price">{{ formatPrice(item.subtotal) }} ₽</div>
                </div>
              </div>
            </div>

            <!-- Summary -->
            <div class="cart-summary">
              <div class="summary-row">
                <span class="summary-label">Стоимость покупки</span>
                <span class="summary-value">{{ formatPrice(shopStore.cart.total_price) }} ₽</span>
              </div>
              <div class="summary-divider" />
              <div class="summary-total-label">Итого, без учёта стоимости доставки</div>
              <div class="summary-total-price">{{ formatPrice(shopStore.cart.total_price) }} ₽</div>
              <button class="summary-continue-btn" @click="activeTab = 'checkout'">Продолжить</button>
            </div>
          </div>
        </template>
      </div>

      <!-- ─── CHECKOUT ──────────────────────────────────────────────────────── -->
      <div v-if="activeTab === 'checkout'">
        <h1 class="page-title">ОФОРМЛЕНИЕ ЗАКАЗА</h1>
        <div class="cart-divider" />

        <div class="cart-layout">
          <!-- Form -->
          <div class="checkout-form">
            <!-- ФИО -->
            <div class="checkout-section">
              <div class="checkout-section__title">Ваше ФИО?</div>
              <div class="checkout-fields">
                <input v-model="orderForm.last_name" class="checkout-input" placeholder="Фамилия" />
                <input v-model="orderForm.first_name" class="checkout-input" placeholder="Имя" />
                <input v-model="orderForm.patronymic" class="checkout-input" placeholder="Отчество" />
                <input v-model="orderForm.contact_channel" class="checkout-input" placeholder="Где можно с вами связаться?" />
              </div>
            </div>

            <!-- Delivery -->
            <div class="checkout-section">
              <div class="checkout-section__title">Как вам удобно получить заказ?</div>
              <div class="delivery-options">
                <label class="delivery-option" :class="{ selected: orderForm.delivery_method === 'delivery' }">
                  <input type="radio" value="delivery" v-model="orderForm.delivery_method" />
                  <span class="delivery-option__radio" />
                  Доставка
                </label>
                <label class="delivery-option" :class="{ selected: orderForm.delivery_method === 'pickup' }">
                  <input type="radio" value="pickup" v-model="orderForm.delivery_method" />
                  <span class="delivery-option__radio" />
                  Самовывоз из Екатеринбурга
                </label>
              </div>
              <p class="delivery-hint" v-if="orderForm.delivery_method === 'pickup'">
                Адрес получения: ул.Мира 19, 10:00–17:00 с понедельника по пятницу
              </p>
              <p class="delivery-hint" v-else>
                Доставка осуществляется через Яндекс. Доставку за вас счёт мы свяжемся с вами!
              </p>
            </div>

            <!-- Payment -->
            <div class="checkout-section">
              <div class="checkout-section__title">Оплата</div>
              <div class="payment-info">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FF6C36" stroke-width="1.8">
                  <rect x="2" y="5" width="20" height="14" rx="2" />
                  <line x1="2" y1="10" x2="22" y2="10" />
                </svg>
                Банковская карта онлайн
              </div>
            </div>
          </div>

          <!-- Summary -->
          <div class="cart-summary">
            <div class="summary-row">
              <span class="summary-label">Стоимость покупки</span>
              <span class="summary-value">{{ formatPrice(shopStore.cart.total_price) }} ₽</span>
            </div>
            <div class="summary-divider" />
            <div class="summary-total-label">Итого, без учёта стоимости доставки</div>
            <div class="summary-total-price">{{ formatPrice(shopStore.cart.total_price) }} ₽</div>
            <button
              class="summary-continue-btn"
              :disabled="submitting || !isFormValid"
              @click="submitOrder"
            >
              {{ submitting ? 'Оформляем...' : 'Перейти к оплате' }}
            </button>
            <p v-if="formError" class="form-error">{{ formError }}</p>
          </div>
        </div>
      </div>

      <!-- ─── ORDERS ────────────────────────────────────────────────────────── -->
      <div v-if="activeTab === 'orders'">
        <h1 class="page-title">МОИ ЗАКАЗЫ</h1>
        <div class="cart-divider" />

        <div v-if="shopStore.loading" class="cart-loading">Загружаем заказы...</div>

        <div v-else-if="shopStore.orders.length === 0" class="empty-cart">
          <p>Заказов пока нет</p>
          <RouterLink to="/shop" class="go-shop-btn">Перейти в каталог</RouterLink>
        </div>

        <div v-else class="orders-list">
          <div v-for="order in shopStore.orders" :key="order.order_id" class="order-card">
            <div class="order-card__header">
              <span class="order-card__id">Заказ #{{ order.order_id }}</span>
              <span class="order-card__status" :class="order.status">{{ statusLabel(order.status) }}</span>
              <span class="order-card__date">{{ formatDate(order.created_at) }}</span>
            </div>
            <div class="order-card__items">
              <span v-for="item in order.items" :key="item.order_item_id" class="order-item-chip">
                {{ item.product_name }} × {{ item.quantity }}
              </span>
            </div>
            <div class="order-card__footer">
              <span class="order-card__total">{{ formatPrice(order.total_price) }} ₽</span>
              <span class="order-card__delivery">{{ order.delivery_method === 'pickup' ? 'Самовывоз' : 'Доставка' }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { baseUrl, useDataStore } from '@/stores/counter'
import { useShopStore } from '@/stores/shop'

const dataStore = useDataStore()
const shopStore = useShopStore()

const isAuthed = computed(() => !!dataStore.auth_key)
const activeTab = ref('cart')

const orderForm = ref({
  last_name: '',
  first_name: '',
  patronymic: '',
  contact_channel: '',
  delivery_method: 'pickup',
  pay_by_card: true,
})

// Автозаполнение формы из данных профиля
function prefillFromProfile() {
  const p = dataStore.profileData
  if (!p) return

  // full_name: "Фамилия Имя Отчество"
  if (p.full_name) {
    const parts = p.full_name.trim().split(/\s+/)
    orderForm.value.last_name  = parts[0] || ''
    orderForm.value.first_name = parts[1] || ''
    orderForm.value.patronymic = parts[2] || ''
  }

  // Контакт: телефон, или email, или telegram
  if (!orderForm.value.contact_channel) {
    orderForm.value.contact_channel =
      p.phone || p.telegram || p.email || ''
  }
}

const submitting = ref(false)
const formError = ref('')

const isFormValid = computed(() =>
  orderForm.value.last_name.trim() &&
  orderForm.value.first_name.trim() &&
  orderForm.value.contact_channel.trim(),
)

function isFavorite(productId) {
  return shopStore.favoriteProductIds.includes(productId)
}

async function toggleFav(product) {
  if (!product) return
  await shopStore.ToggleFavorite(dataStore.auth_key, product.product_id)
}

onMounted(async () => {
  if (isAuthed.value) {
    await shopStore.FetchCart(dataStore.auth_key)
    // Загружаем профиль если ещё не загружен
    if (!dataStore.profileData?.full_name) {
      try { await dataStore.GetProfile() } catch {}
    }
    prefillFromProfile()
  }
})

// Если профиль пришёл позже (напр. после асинхронной загрузки) — подставляем данные
watch(() => dataStore.profileData, prefillFromProfile, { deep: true })

async function loadOrders() {
  activeTab.value = 'orders'
  if (isAuthed.value) {
    await shopStore.FetchOrders(dataStore.auth_key)
  }
}

async function updateQty(item, newQty) {
  if (newQty < 1 || newQty > item.available) return
  await shopStore.UpdateCartItem(dataStore.auth_key, item.cart_item_id, newQty)
}

async function removeItem(item) {
  await shopStore.RemoveFromCart(dataStore.auth_key, item.cart_item_id)
}

async function submitOrder() {
  if (!isFormValid.value) return
  submitting.value = true
  formError.value = ''
  try {
    await shopStore.CreateOrder(dataStore.auth_key, { ...orderForm.value })
    activeTab.value = 'orders'
    await shopStore.FetchOrders(dataStore.auth_key)
  } catch (err) {
    formError.value = err.response?.data?.message || 'Ошибка при оформлении'
  } finally {
    submitting.value = false
  }
}

function formatPrice(price) {
  return Number(price).toLocaleString('ru-RU')
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}

function statusLabel(status) {
  const labels = {
    new: 'Новый',
    awaiting_payment: 'Ожидает оплаты',
    paid: 'Оплачен',
    cancelled: 'Отменён',
    completed: 'Выдан',
  }
  return labels[status] || status
}
</script>

<style scoped>
.orders-page {
  max-width: 960px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

/* ── Auth prompt ── */
.auth-prompt {
  text-align: center;
  padding: 80px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.auth-prompt h2 { font-size: 22px; color: #1a1a1a; margin: 0; }
.auth-prompt p  { color: #888; margin: 0; }
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
.auth-prompt__btn:hover { background: #DD5827; }

/* ── Tabs ── */
.orders-tabs {
  display: flex;
  border-bottom: 2px solid #e8e5e0;
}
.orders-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  background: none;
  font-size: 15px;
  font-weight: 500;
  color: #888;
  cursor: pointer;
  position: relative;
  transition: color 0.2s;
}
.orders-tab.active { color: #FF6C36; }
.orders-tab.active::after {
  content: '';
  position: absolute;
  bottom: -2px; left: 0; right: 0;
  height: 2px;
  background: #FF6C36;
  border-radius: 2px 2px 0 0;
}
.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px; height: 20px;
  padding: 0 6px;
  border-radius: 10px;
  background: #FF6C36;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
}

/* ── Page title ── */
.page-title {
  font-size: 26px;
  font-weight: 900;
  color: #1a1a1a;
  letter-spacing: 0.02em;
  margin: 0 0 16px;
}
.cart-divider {
  border: none;
  border-top: 1.5px solid #e8e5e0;
  margin-bottom: 28px;
}

/* ── Layout ── */
.cart-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 32px;
  align-items: start;
}

/* ── Cart items ── */
.cart-items {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.cart-item {
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: 24px;
  padding: 24px 0;
  border-bottom: 1px solid #e8e5e0;
}
.cart-item:first-child { border-top: none; }

.cart-item__img-wrap {
  width: 180px;
  height: 200px;
  border-radius: 10px;
  overflow: hidden;
  background: #f5f3f0;
  flex-shrink: 0;
}
.cart-item__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.cart-item__img-placeholder {
  width: 100%;
  height: 100%;
  background: #eee;
}

.cart-item__body {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.cart-item__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}
.cart-item__name {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  text-decoration: none;
  line-height: 1.35;
  flex: 1;
}
.cart-item__name:hover { color: #FF6C36; }

.cart-item__actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}
.cart-item__action-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1.5px solid #e0ddd8;
  background: #fff;
  color: #aaa;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s, border-color 0.2s, background 0.2s;
}
.cart-item__action-btn:hover {
  border-color: #FF6C36;
  color: #FF6C36;
}
.cart-item__action-btn.fav { color: #FF6C36; border-color: #FF6C36; }
.cart-item__action-btn.delete:hover { border-color: #ef4444; color: #ef4444; }

.cart-item__meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
  color: #555;
  font-size: 14px;
  margin-top: 2px;
}

/* Qty */
.cart-item__qty {
  display: flex;
  align-items: center;
  gap: 0;
  margin-top: 8px;
  border: 1.5px solid #e0ddd8;
  border-radius: 8px;
  width: fit-content;
  overflow: hidden;
}
.qty-btn {
  width: 34px;
  height: 34px;
  border: none;
  background: #fff;
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  color: #555;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, color 0.15s;
}
.qty-btn:hover:not(:disabled) { background: #f5f3f0; color: #1a1a1a; }
.qty-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.qty-val {
  font-size: 15px;
  font-weight: 600;
  min-width: 36px;
  text-align: center;
  border-left: 1.5px solid #e0ddd8;
  border-right: 1.5px solid #e0ddd8;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cart-item__price {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a1a;
  margin-top: 10px;
}

/* ── Summary ── */
.cart-summary {
  background: #f7f6f3;
  border-radius: 14px;
  padding: 22px 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  position: sticky;
  top: 84px;
}
.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #555;
}
.summary-value { font-weight: 600; color: #1a1a1a; }
.summary-divider {
  border: none;
  border-top: 1px solid #e0ddd8;
  margin: 4px 0;
}
.summary-total-label { font-size: 13px; color: #888; }
.summary-total-price {
  font-size: 22px;
  font-weight: 800;
  color: #1a1a1a;
  letter-spacing: -0.01em;
}
.summary-continue-btn {
  margin-top: 6px;
  width: 100%;
  padding: 14px;
  border-radius: 10px;
  border: none;
  background: #FF6C36;
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s, transform 0.15s;
  letter-spacing: 0.01em;
}
.summary-continue-btn:hover:not(:disabled) {
  background: #DD5827;
  transform: translateY(-1px);
}
.summary-continue-btn:disabled { background: #ccc; cursor: not-allowed; transform: none; }

/* ── Checkout form ── */
.checkout-form {
  display: flex;
  flex-direction: column;
  gap: 32px;
}
.checkout-section__title {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 14px;
}
.checkout-fields {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.checkout-input {
  padding: 12px 14px;
  border-radius: 8px;
  border: 1.5px solid #e0ddd8;
  font-size: 14px;
  color: #1a1a1a;
  background: #fff;
  outline: none;
  transition: border-color 0.2s;
  width: 100%;
  box-sizing: border-box;
}
.checkout-input::placeholder { color: #bbb; }
.checkout-input:focus { border-color: #FF6C36; }

/* Delivery / Payment options */
.delivery-options {
  border: 1.5px solid #e0ddd8;
  border-radius: 10px;
  overflow: hidden;
}
.delivery-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  cursor: pointer;
  font-size: 14px;
  color: #1a1a1a;
  background: #fff;
  transition: background 0.15s;
  border-bottom: 1px solid #e0ddd8;
}
.delivery-option:last-child { border-bottom: none; }
.delivery-option:hover { background: #fafaf8; }
.delivery-option input[type="radio"] { display: none; }

.delivery-option__radio {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid #d0cdc8;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.2s;
  position: relative;
}
.delivery-option.selected .delivery-option__radio {
  border-color: #FF6C36;
}
.delivery-option.selected .delivery-option__radio::after {
  content: '';
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #FF6C36;
  position: absolute;
}

.pay-icon {
  margin-left: auto;
  display: flex;
  align-items: center;
}

.payment-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  border: 1.5px solid #e0ddd8;
  border-radius: 10px;
  background: #fff;
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
}

.delivery-hint {
  font-size: 13px;
  color: #666;
  margin: 10px 0 0;
  line-height: 1.5;
}

/* ── Empty / Loading ── */
.cart-loading,
.empty-cart {
  text-align: center;
  padding: 60px;
  color: #999;
  font-size: 15px;
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
.go-shop-btn:hover { background: #DD5827; }

.form-error {
  color: #ef4444;
  font-size: 13px;
  margin: 0;
  text-align: center;
}

/* ── Orders list ── */
.orders-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.order-card {
  background: #fff;
  border-radius: 14px;
  padding: 20px;
  border: 1px solid #f0ede8;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.order-card__header {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.order-card__id { font-size: 15px; font-weight: 700; color: #1a1a1a; }
.order-card__date { font-size: 13px; color: #999; margin-left: auto; }
.order-card__status {
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.order-card__status.new              { background: #e0f2fe; color: #0284c7; }
.order-card__status.awaiting_payment { background: #fef3c7; color: #d97706; }
.order-card__status.paid             { background: #dcfce7; color: #16a34a; }
.order-card__status.cancelled        { background: #fee2e2; color: #dc2626; }
.order-card__status.completed        { background: #f3e8ff; color: #9333ea; }
.order-card__items { display: flex; flex-wrap: wrap; gap: 6px; }
.order-item-chip {
  font-size: 12px;
  background: #f0ede8;
  color: #555;
  padding: 4px 10px;
  border-radius: 6px;
}
.order-card__footer { display: flex; align-items: center; justify-content: space-between; }
.order-card__total { font-size: 17px; font-weight: 700; }
.order-card__delivery { font-size: 13px; color: #888; }

/* ── Responsive ── */
@media (max-width: 768px) {
  .cart-layout {
    grid-template-columns: 1fr;
  }
  .cart-item {
    grid-template-columns: 120px 1fr;
    gap: 16px;
  }
  .cart-item__img-wrap {
    width: 120px;
    height: 140px;
  }
  .page-title { font-size: 20px; }
}

@media (max-width: 480px) {
  .cart-item {
    grid-template-columns: 90px 1fr;
    gap: 12px;
  }
  .cart-item__img-wrap {
    width: 90px;
    height: 110px;
  }
  .cart-item__price { font-size: 18px; }
}
</style>
