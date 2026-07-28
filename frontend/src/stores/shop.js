import { defineStore } from 'pinia'
import axios from 'axios'
import { baseUrl } from '@/stores/counter'

function hasProductImage(product) {
  if (!product) return false
  if (product.main_image) return true
  if (product.images && product.images.length > 0) return true
  return false
}

export const useShopStore = defineStore('shop', {
  state: () => ({
    banners: [],
    categories: [],
    products: [],
    productDetail: null,
    cart: { items: [], total_price: '0' },
    favorites: [],
    orders: [],
    loading: false,
    cartLoading: false,
  }),

  getters: {
    cartItemsCount: (state) => state.cart.items.reduce((sum, item) => sum + item.quantity, 0),
    favoritesCount: (state) => state.favorites.length,
    favoriteProductIds: (state) => state.favorites.map(f => f.product?.product_id).filter(Boolean),
  },

  actions: {
    async FetchHome() {
      this.loading = true
      try {
        const response = await axios.get(`${baseUrl}api/user/merch`)
        this.banners = response.data.banners || []
        this.categories = response.data.categories || []
        this.products = response.data.products || []
      } catch (error) {
        console.error('Ошибка при загрузке главной магазина:', error.response?.data || error.message)
        throw error
      } finally {
        this.loading = false
      }
    },

    async FetchProducts(categoryId = null, search = null) {
      this.loading = true
      try {
        let cat = categoryId
        let q = search
        if (categoryId && typeof categoryId === 'object') {
          cat = categoryId.categoryId || categoryId.category_id || null
          q = categoryId.search || categoryId.q || null
        }
        const params = {}
        if (cat) params.category_id = cat
        if (q) params.search = q
        const response = await axios.get(`${baseUrl}api/user/merch/products`, { params })
        this.products = response.data.products || []
      } catch (error) {
        console.error('Ошибка при загрузке товаров:', error.response?.data || error.message)
        throw error
      } finally {
        this.loading = false
      }
    },

    async FetchProductDetail(productId) {
      this.loading = true
      this.productDetail = null
      try {
        const response = await axios.get(`${baseUrl}api/user/merch/products/${productId}`)
        this.productDetail = response.data
      } catch (error) {
        console.error('Ошибка при загрузке товара:', error.response?.data || error.message)
        throw error
      } finally {
        this.loading = false
      }
    },

    async FetchCart(authKey) {
      this.cartLoading = true
      try {
        const response = await axios.get(`${baseUrl}api/user/merch/cart`, {
          headers: { Authorization: `Bearer ${authKey}` },
        })
        const cartData = response.data
        if (cartData && cartData.items) {
          cartData.items = cartData.items.filter(item => hasProductImage(item.product))
        }
        this.cart = cartData
      } catch (error) {
        console.error('Ошибка при загрузке корзины:', error.response?.data || error.message)
        throw error
      } finally {
        this.cartLoading = false
      }
    },

    async AddToCart(authKey, variantId, quantity = 1) {
      try {
        await axios.post(
          `${baseUrl}api/user/merch/cart`,
          { variant_id: variantId, quantity },
          { headers: { Authorization: `Bearer ${authKey}`, 'Content-Type': 'application/json' } },
        )
        await this.FetchCart(authKey)
      } catch (error) {
        console.error('Ошибка при добавлении в корзину:', error.response?.data || error.message)
        throw error
      }
    },

    async UpdateCartItem(authKey, cartItemId, quantity) {
      try {
        await axios.put(
          `${baseUrl}api/user/merch/cart/${cartItemId}`,
          { quantity },
          { headers: { Authorization: `Bearer ${authKey}`, 'Content-Type': 'application/json' } },
        )
        await this.FetchCart(authKey)
      } catch (error) {
        console.error('Ошибка при изменении количества:', error.response?.data || error.message)
        throw error
      }
    },

    async RemoveFromCart(authKey, cartItemId) {
      try {
        await axios.delete(`${baseUrl}api/user/merch/cart/${cartItemId}`, {
          headers: { Authorization: `Bearer ${authKey}` },
        })
        await this.FetchCart(authKey)
      } catch (error) {
        console.error('Ошибка при удалении из корзины:', error.response?.data || error.message)
        throw error
      }
    },

    async FetchFavorites(authKey) {
      try {
        const response = await axios.get(`${baseUrl}api/user/merch/favorites`, {
          headers: { Authorization: `Bearer ${authKey}` },
        })
        this.favorites = (response.data.favorites || []).filter(fav => hasProductImage(fav.product))
      } catch (error) {
        console.error('Ошибка при загрузке избранного:', error.response?.data || error.message)
        throw error
      }
    },

    async ToggleFavorite(authKey, productId) {
      try {
        const response = await axios.post(
          `${baseUrl}api/user/merch/products/${productId}/favorite`,
          {},
          { headers: { Authorization: `Bearer ${authKey}` } },
        )
        const product = this.products.find((p) => p.product_id === productId)
        if (product) product.is_favorite = response.data.is_favorite
        if (this.productDetail?.product_id === productId) {
          this.productDetail.is_favorite = response.data.is_favorite
        }
        await this.FetchFavorites(authKey)
        return response.data.is_favorite
      } catch (error) {
        console.error('Ошибка при изменении избранного:', error.response?.data || error.message)
        throw error
      }
    },

    async FetchOrders(authKey) {
      this.loading = true
      try {
        const response = await axios.get(`${baseUrl}api/user/merch/orders`, {
          headers: { Authorization: `Bearer ${authKey}` },
        })
        this.orders = response.data.orders || []
      } catch (error) {
        console.error('Ошибка при загрузке заказов:', error.response?.data || error.message)
        throw error
      } finally {
        this.loading = false
      }
    },

    async CreateOrder(authKey, orderData) {
      try {
        const response = await axios.post(`${baseUrl}api/user/merch/orders`, orderData, {
          headers: { Authorization: `Bearer ${authKey}`, 'Content-Type': 'application/json' },
        })
        const order = response.data.order
        if (order.payment_url) {
          window.location.href = order.payment_url
        }
        this.cart = { items: [], total_price: '0' }
        return order
      } catch (error) {
        console.error('Ошибка при оформлении заказа:', error.response?.data || error.message)
        throw error
      }
    },
  },
})
