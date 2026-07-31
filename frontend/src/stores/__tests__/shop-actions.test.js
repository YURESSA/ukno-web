import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('axios')
vi.mock('@/stores/counter', () => ({ baseUrl: 'http://localhost:8000/' }))

import axios from 'axios'
import { useShopStore } from '@/stores/shop'

describe('ShopStore — действия магазина', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('добавляет вариант в корзину и затем обновляет корзину', async () => {
    axios.post.mockResolvedValueOnce({ data: { item: { cart_item_id: 4 } } })
    axios.get.mockResolvedValueOnce({ data: { items: [], total_price: '0' } })
    const store = useShopStore()

    await store.AddToCart('token', 17, 2)

    expect(axios.post).toHaveBeenCalledWith(
      'http://localhost:8000/api/user/merch/cart',
      { variant_id: 17, quantity: 2 },
      { headers: { Authorization: 'Bearer token', 'Content-Type': 'application/json' } },
    )
    expect(axios.get).toHaveBeenCalledWith(
      'http://localhost:8000/api/user/merch/cart',
      { headers: { Authorization: 'Bearer token' } },
    )
  })

  it('обновляет количество позиции и повторно загружает корзину', async () => {
    axios.put.mockResolvedValueOnce({ data: {} })
    axios.get.mockResolvedValueOnce({ data: { items: [], total_price: '0' } })
    const store = useShopStore()

    await store.UpdateCartItem('token', 8, 3)

    expect(axios.put).toHaveBeenCalledWith(
      'http://localhost:8000/api/user/merch/cart/8',
      { quantity: 3 },
      { headers: { Authorization: 'Bearer token', 'Content-Type': 'application/json' } },
    )
  })

  it('удаляет позицию и повторно загружает корзину', async () => {
    axios.delete.mockResolvedValueOnce({ data: {} })
    axios.get.mockResolvedValueOnce({ data: { items: [], total_price: '0' } })
    const store = useShopStore()

    await store.RemoveFromCart('token', 8)

    expect(axios.delete).toHaveBeenCalledWith(
      'http://localhost:8000/api/user/merch/cart/8',
      { headers: { Authorization: 'Bearer token' } },
    )
  })

  it('синхронизирует избранное в каталоге и карточке товара', async () => {
    axios.post.mockResolvedValueOnce({ data: { is_favorite: true } })
    axios.get.mockResolvedValueOnce({ data: { favorites: [] } })
    const store = useShopStore()
    store.products = [{ product_id: 31, is_favorite: false }]
    store.productDetail = { product_id: 31, is_favorite: false }

    const result = await store.ToggleFavorite('token', 31)

    expect(result).toBe(true)
    expect(store.products[0].is_favorite).toBe(true)
    expect(store.productDetail.is_favorite).toBe(true)
    expect(axios.post).toHaveBeenCalledWith(
      'http://localhost:8000/api/user/merch/products/31/favorite',
      {},
      { headers: { Authorization: 'Bearer token' } },
    )
  })

  it('после создания заказа очищает корзину и возвращает заказ', async () => {
    const order = { order_id: 22, payment_url: null, status: 'new' }
    axios.post.mockResolvedValueOnce({ data: { order } })
    const store = useShopStore()
    store.cart = { items: [{ cart_item_id: 1 }], total_price: '2500.00' }
    const payload = {
      last_name: 'Иванов',
      first_name: 'Иван',
      contact_channel: '@ivan',
      delivery_method: 'pickup',
      pay_by_card: false,
    }

    await expect(store.CreateOrder('token', payload)).resolves.toEqual(order)
    expect(store.cart).toEqual({ items: [], total_price: '0' })
    expect(axios.post).toHaveBeenCalledWith(
      'http://localhost:8000/api/user/merch/orders',
      payload,
      { headers: { Authorization: 'Bearer token', 'Content-Type': 'application/json' } },
    )
  })
})
