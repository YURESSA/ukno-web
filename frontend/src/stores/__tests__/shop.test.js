import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { createTestingPinia } from '@pinia/testing'

vi.mock('axios')
import axios from 'axios'

vi.mock('@/stores/counter', () => ({
  baseUrl: 'http://localhost:8000/',
}))

import { useShopStore } from '@/stores/shop'

describe('ShopStore — геттеры', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('cartItemsCount: возвращает суммарное количество единиц товаров в корзине', () => {
    const store = useShopStore()

    store.cart = {
      items: [
        { product_id: 1, quantity: 2 },
        { product_id: 2, quantity: 3 },
      ],
      total_price: '5000',
    }

    expect(store.cartItemsCount).toBe(5)
  })

  it('cartItemsCount: возвращает 0 при пустой корзине', () => {
    const store = useShopStore()
    expect(store.cartItemsCount).toBe(0)
  })

  it('favoritesCount: возвращает точное количество позиций в избранном', () => {
    const store = useShopStore()
    store.favorites = [
      { id: 1, product: { product_id: 10 } },
      { id: 2, product: { product_id: 20 } },
      { id: 3, product: { product_id: 30 } },
    ]

    expect(store.favoritesCount).toBe(3)
  })

  it('favoriteProductIds: возвращает массив только product_id из избранного', () => {
    const store = useShopStore()
    store.favorites = [
      { id: 1, product: { product_id: 101 } },
      { id: 2, product: { product_id: 202 } },
      { id: 3, product: null },
    ]

    const ids = store.favoriteProductIds
    expect(ids).toEqual([101, 202])
    expect(ids).not.toContain(null)
    expect(ids).not.toContain(undefined)
  })

  it('favoriteProductIds: возвращает пустой массив при пустом favorites', () => {
    const store = useShopStore()
    expect(store.favoriteProductIds).toEqual([])
  })
})

describe('ShopStore — FetchProducts', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('передаёт category_id и search в параметры axios.get', async () => {
    const mockProducts = [{ product_id: 1, name: 'Футболка' }]
    axios.get.mockResolvedValueOnce({ data: { products: mockProducts } })

    const store = useShopStore()
    await store.FetchProducts(5, 'футболка')

    expect(axios.get).toHaveBeenCalledWith(
      'http://localhost:8000/api/user/merch/products',
      { params: { category_id: 5, search: 'футболка' } },
    )
  })

  it('сохраняет полученные товары в state.products', async () => {
    const mockProducts = [
      { product_id: 1, name: 'Кружка' },
      { product_id: 2, name: 'Шоппер' },
    ]
    axios.get.mockResolvedValueOnce({ data: { products: mockProducts } })

    const store = useShopStore()
    await store.FetchProducts()

    expect(store.products).toEqual(mockProducts)
    expect(store.products).toHaveLength(2)
  })

  it('выставляет loading = true во время запроса, false после завершения', async () => {
    let resolveRequest
    const pendingPromise = new Promise((resolve) => {
      resolveRequest = resolve
    })
    axios.get.mockReturnValueOnce(pendingPromise)

    const store = useShopStore()
    const actionPromise = store.FetchProducts()

    expect(store.loading).toBe(true)

    resolveRequest({ data: { products: [] } })
    await actionPromise

    expect(store.loading).toBe(false)
  })

  it('при сетевой ошибке: loading сбрасывается в false и ошибка пробрасывается', async () => {
    const networkError = new Error('Network Error')
    axios.get.mockRejectedValueOnce(networkError)

    const store = useShopStore()

    await expect(store.FetchProducts()).rejects.toThrow('Network Error')

    expect(store.loading).toBe(false)
  })

  it('при отсутствии products в ответе: state.products становится пустым массивом', async () => {
    axios.get.mockResolvedValueOnce({ data: {} })

    const store = useShopStore()
    await store.FetchProducts()

    expect(store.products).toEqual([])
  })
})

describe('ShopStore — FetchHome', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('сохраняет banners, categories и products из ответа сервера', async () => {
    const mockResponse = {
      banners: [{ id: 1, image: 'banner.jpg' }],
      categories: [{ id: 1, name: 'Одежда' }],
      products: [{ product_id: 1, name: 'Худи' }],
    }
    axios.get.mockResolvedValueOnce({ data: mockResponse })

    const store = useShopStore()
    await store.FetchHome()

    expect(store.banners).toEqual(mockResponse.banners)
    expect(store.categories).toEqual(mockResponse.categories)
    expect(store.products).toEqual(mockResponse.products)
    expect(store.loading).toBe(false)
  })
})

describe('ShopStore — hasProductImage (через FetchCart)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('FetchCart отфильтровывает товары без изображений из корзины', async () => {
    const cartWithMixedItems = {
      total_price: '3000',
      items: [
        {
          cart_item_id: 1,
          quantity: 1,
          product: { product_id: 1, name: 'Кепка', main_image: '/media/cap.jpg' },
        },
        {
          cart_item_id: 2,
          quantity: 2,
          product: { product_id: 2, name: 'Удалённый товар' },
        },
        {
          cart_item_id: 3,
          quantity: 1,
          product: { product_id: 3, name: 'Шоппер', images: [{ image_path: '/media/bag.jpg' }] },
        },
      ],
    }
    axios.get.mockResolvedValueOnce({ data: cartWithMixedItems })

    const store = useShopStore()
    await store.FetchCart('test-auth-key')

    expect(store.cart.items).toHaveLength(2)
    expect(store.cart.items.map((i) => i.product.product_id)).toEqual([1, 3])
  })
})
