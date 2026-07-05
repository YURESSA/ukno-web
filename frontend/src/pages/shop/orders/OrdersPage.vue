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
          :class="{ active: activeTab === 'cart' }"
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

      <!-- CART TAB -->
      <div v-if="activeTab === 'cart'">
        <div v-if="shopStore.cartLoading" class="cart-loading">Загружаем корзину...</div>

        <div v-else-if="shopStore.cart.items.length === 0" class="empty-cart">
          <p>Корзина пуста</p>
          <RouterLink to="/shop" class="go-shop-btn">Перейти в каталог</RouterLink>
        </div>

        <template v-else>
          <div class="cart-items">
            <div
              v-for="item in shopStore.cart.items"
              :key="item.cart_item_id"
              class="cart-item"
            >
              <div class="cart-item__img-wrap">
                <img
                  v-if="item.product?.main_image"
                  :src="baseUrl + item.product.main_image"
                  :alt="item.product?.name"
                  class="cart-item__img"
                />
                <div v-else class="cart-item__img-placeholder" />
              </div>

              <div class="cart-item__info">
                <RouterLink :to="`/shop/${item.product?.product_id}`" class="cart-item__name">
                  {{ item.product?.name }}
                </RouterLink>
                <div class="cart-item__meta">
                  <span v-if="item.color" class="cart-item__meta-chip">{{ item.color.name }}</span>
                  <span v-if="item.size" class="cart-item__meta-chip">{{ item.size.name }}</span>
                </div>
                <span class="cart-item__subtotal">{{ formatPrice(item.subtotal) }} ₽</span>
              </div>

              <div class="cart-item__qty">
                <button class="qty-btn" @click="updateQty(item, item.quantity - 1)" :disabled="item.quantity <= 1">−</button>
                <span class="qty-val">{{ item.quantity }}</span>
                <button class="qty-btn" @click="updateQty(item, item.quantity + 1)" :disabled="item.quantity >= item.available">+</button>
              </div>

              <button class="cart-item__remove" @click="removeItem(item)" title="Удалить">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6" />
                  <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
                  <path d="M10 11v6M14 11v6" />
                  <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Cart summary & checkout -->
          <div class="cart-summary">
            <div class="cart-total">
              <span>Итого:</span>
              <strong>{{ formatPrice(shopStore.cart.total_price) }} ₽</strong>
            </div>

            <div class="checkout-form">
              <h3 class="checkout-form__title">Оформление заказа</h3>
              <div class="form-row">
                <input v-model="orderForm.last_name" class="form-input" placeholder="Фамилия *" />
                <input v-model="orderForm.first_name" class="form-input" placeholder="Имя *" />
              </div>
              <input v-model="orderForm.patronymic" class="form-input" placeholder="Отчество" />
              <input
                v-model="orderForm.contact_channel"
                class="form-input"
                placeholder="Контакт: телефон / Telegram *"
              />

              <div class="pay-options">
                <label class="pay-option" :class="{ selected: !orderForm.pay_by_card }">
                  <input type="radio" :value="false" v-model="orderForm.pay_by_card" />
                  Наличными при получении
                </label>
                <label class="pay-option" :class="{ selected: orderForm.pay_by_card }">
                  <input type="radio" :value="true" v-model="orderForm.pay_by_card" />
                  Оплатить картой онлайн
                </label>
              </div>

              <button
                class="checkout-btn"
                :disabled="submitting || !isFormValid"
                @click="submitOrder"
              >
                {{ submitting ? 'Оформляем...' : 'Оформить заказ' }}
              </button>
              <p v-if="formError" class="form-error">{{ formError }}</p>
            </div>
          </div>
        </template>
      </div>

      <!-- ORDERS TAB -->
      <div v-if="activeTab === 'orders'">
        <div v-if="shopStore.loading" class="cart-loading">Загружаем заказы...</div>

        <div v-else-if="shopStore.orders.length === 0" class="empty-cart">
          <p>Заказов пока нет</p>
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
              <span class="order-card__delivery">{{ order.delivery_method === 'pickup' ? 'Самовывоз' : order.delivery_method }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
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
  pay_by_card: false,
})

const submitting = ref(false)
const formError = ref('')

const isFormValid = computed(() =>
  orderForm.value.last_name.trim() &&
  orderForm.value.first_name.trim() &&
  orderForm.value.contact_channel.trim(),
)

onMounted(async () => {
  if (isAuthed.value) {
    await shopStore.FetchCart(dataStore.auth_key)
  }
})

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
    await shopStore.CreateOrder(dataStore.auth_key, {
      ...orderForm.value,
    })
    // Если нет редиректа на оплату — переходим в заказы
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
  max-width: 860px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

/* Auth prompt */
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

/* Tabs */
.orders-tabs {
  display: flex;
  border-bottom: 2px solid #e8e5e0;
  gap: 0;
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

.orders-tab.active {
  color: #FF6C36;
}

.orders-tab.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: #FF6C36;
  border-radius: 2px 2px 0 0;
}

.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 10px;
  background: #FF6C36;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
}

/* Cart items */
.cart-loading,
.empty-cart {
  text-align: center;
  padding: 60px;
  color: #999;
  font-size: 15px;
}

.cart-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.cart-item {
  display: grid;
  grid-template-columns: 80px 1fr auto auto;
  align-items: center;
  gap: 16px;
  background: #fff;
  border-radius: 14px;
  padding: 16px;
  border: 1px solid #f0ede8;
}

.cart-item__img-wrap {
  width: 80px;
  height: 80px;
  border-radius: 10px;
  overflow: hidden;
  flex-shrink: 0;
  background: #f5f3f0;
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

.cart-item__info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cart-item__name {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
  text-decoration: none;
}

.cart-item__name:hover {
  color: #FF6C36;
}

.cart-item__meta {
  display: flex;
  gap: 6px;
}

.cart-item__meta-chip {
  font-size: 12px;
  color: #888;
  background: #f0ede8;
  padding: 2px 8px;
  border-radius: 4px;
}

.cart-item__subtotal {
  font-size: 15px;
  font-weight: 700;
  color: #1a1a1a;
}

.cart-item__qty {
  display: flex;
  align-items: center;
  gap: 8px;
}

.qty-btn {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: 1px solid #e0ddd8;
  background: #fff;
  font-size: 18px;
  line-height: 1;
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
  opacity: 0.3;
  cursor: not-allowed;
}

.qty-val {
  font-size: 15px;
  font-weight: 600;
  min-width: 20px;
  text-align: center;
}

.cart-item__remove {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  border: none;
  background: none;
  color: #ccc;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s, background 0.2s;
}

.cart-item__remove:hover {
  color: #ef4444;
  background: #fef2f2;
}

/* Summary */
.cart-summary {
  background: #fff;
  border-radius: 16px;
  padding: 28px;
  border: 1px solid #f0ede8;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.cart-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
}

.cart-total strong {
  font-size: 22px;
  font-weight: 700;
}

/* Checkout form */
.checkout-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checkout-form__title {
  font-size: 17px;
  font-weight: 700;
  margin: 0;
  color: #1a1a1a;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-input {
  padding: 11px 14px;
  border-radius: 10px;
  border: 1.5px solid #e0ddd8;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.form-input:focus {
  border-color: #FF6C36;
}

/* Pay options */
.pay-options {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.pay-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 10px;
  border: 1.5px solid #e0ddd8;
  cursor: pointer;
  font-size: 14px;
  color: #555;
  transition: border-color 0.2s, color 0.2s;
}

.pay-option.selected {
  border-color: #FF6C36;
  color: #FF6C36;
}

.pay-option input {
  display: none;
}

.checkout-btn {
  padding: 14px;
  border-radius: 12px;
  border: none;
  background: #FF6C36;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.checkout-btn:hover:not(:disabled) {
  background: #DD5827;
}

.checkout-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.form-error {
  color: #ef4444;
  font-size: 13px;
  margin: 0;
}

/* Orders list */
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

.order-card__id {
  font-size: 15px;
  font-weight: 700;
  color: #1a1a1a;
}

.order-card__status {
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.order-card__status.new          { background: #e0f2fe; color: #0284c7; }
.order-card__status.awaiting_payment { background: #fef3c7; color: #d97706; }
.order-card__status.paid         { background: #dcfce7; color: #16a34a; }
.order-card__status.cancelled    { background: #fee2e2; color: #dc2626; }
.order-card__status.completed    { background: #f3e8ff; color: #9333ea; }

.order-card__date {
  font-size: 13px;
  color: #999;
  margin-left: auto;
}

.order-card__items {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.order-item-chip {
  font-size: 12px;
  background: #f0ede8;
  color: #555;
  padding: 4px 10px;
  border-radius: 6px;
}

.order-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.order-card__total {
  font-size: 17px;
  font-weight: 700;
}

.order-card__delivery {
  font-size: 13px;
  color: #888;
}

.go-shop-btn {
  display: inline-block;
  margin-top: 12px;
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

@media (max-width: 600px) {
  .cart-item {
    grid-template-columns: 64px 1fr;
    grid-template-rows: auto auto;
  }

  .cart-item__qty {
    grid-column: 2;
  }

  .cart-item__remove {
    position: absolute;
    top: 12px;
    right: 12px;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
