import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'

const mocks = vi.hoisted(() => ({
  route: { params: { id: '42' } },
  router: { push: vi.fn(), back: vi.fn() },
  data: { auth_key: 'token' },
  shop: {
    loading: false, productDetail: null, cart: { items: [] }, favoriteProductIds: [],
    FetchProductDetail: vi.fn(), AddToCart: vi.fn(), UpdateCartItem: vi.fn(),
    RemoveFromCart: vi.fn(), ToggleFavorite: vi.fn(),
  },
}))
vi.mock('vue-router', () => ({ useRoute: () => mocks.route, useRouter: () => mocks.router }))
vi.mock('@/stores/counter', () => ({ baseUrl: '/api/', useDataStore: () => mocks.data }))
vi.mock('@/stores/shop', () => ({ useShopStore: () => mocks.shop }))

import ProductDetail from '@/pages/shop/product/ProductDetail.vue'

const product = () => ({
  product_id: 42, name: 'Hoodie', price: '3500', description: 'Warm',
  main_image: 'main.jpg', images: [{ image_path: 'main.jpg' }, { image_path: 'back.jpg' }],
  is_favorite: false,
  colors: [
    { color_id: 1, name: 'Black', available: 3, sizes: [
      { variant_id: 11, size: { name: 'M' }, stock: 3 },
      { variant_id: 12, size: { name: 'L' }, stock: 0 },
    ] },
  ],
})

const mountPage = () => mount(ProductDetail, { global: { stubs: { RouterLink: true } } })

describe('ProductDetail', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    mocks.data.auth_key = 'token'
    Object.assign(mocks.shop, {
      loading: false, productDetail: product(), cart: { items: [] }, favoriteProductIds: [],
    })
    mocks.shop.FetchProductDetail.mockResolvedValue()
    mocks.shop.AddToCart.mockResolvedValue()
    mocks.shop.UpdateCartItem.mockResolvedValue()
    mocks.shop.RemoveFromCart.mockResolvedValue()
  })

  it('загружает товар, выбирает доступный вариант и строит галерею без дублей', async () => {
    const wrapper = mountPage()
    await flushPromises()
    expect(mocks.shop.FetchProductDetail).toHaveBeenCalledWith('42')
    expect(wrapper.findAll('.product-gallery__slide')).toHaveLength(2)
    expect(wrapper.find('.size-btn.active').text()).toContain('M')
  })

  it('циклически переключает изображения и полноэкранный просмотр', async () => {
    const wrapper = mountPage()
    await flushPromises()
    await wrapper.find('.gallery-arrow--next').trigger('click')
    expect(wrapper.find('.product-gallery__track').attributes('style')).toContain('-100%')
    await wrapper.find('.gallery-zoom-btn').trigger('click')
    expect(document.body.querySelector('.fullscreen-gallery-modal')).not.toBeNull()
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    await wrapper.vm.$nextTick()
    expect(document.body.querySelector('.fullscreen-gallery-modal')).toBeNull()
  })

  it('добавляет выбранный вариант в корзину', async () => {
    const wrapper = mountPage()
    await flushPromises()
    await wrapper.find('.product-add-btn').trigger('click')
    expect(mocks.shop.AddToCart).toHaveBeenCalledWith('token', 11, 1)
  })

  it('перенаправляет гостя на login вместо корзины и избранного', async () => {
    mocks.data.auth_key = null
    const wrapper = mountPage()
    await flushPromises()
    await wrapper.find('.product-add-btn').trigger('click')
    const favoriteButton = wrapper.find('.product-fav-btn')
    await favoriteButton.trigger('click')
    expect(mocks.router.push).toHaveBeenCalledWith('/login')
    expect(mocks.shop.AddToCart).not.toHaveBeenCalled()
  })

  it('обновляет и удаляет уже добавленную позицию', async () => {
    mocks.shop.cart = { items: [{ cart_item_id: 8, variant_id: 11, quantity: 2 }] }
    const wrapper = mountPage()
    await flushPromises()
    const qtyButtons = wrapper.findAll('.qty-btn')
    await qtyButtons[1].trigger('click')
    await qtyButtons[0].trigger('click')
    expect(mocks.shop.UpdateCartItem).toHaveBeenCalledWith('token', 8, 3)
    expect(mocks.shop.UpdateCartItem).toHaveBeenCalledWith('token', 8, 1)
  })

  it('переключает избранное авторизованного пользователя', async () => {
    const wrapper = mountPage()
    await flushPromises()
    await wrapper.find('.product-fav-btn').trigger('click')
    expect(mocks.shop.ToggleFavorite).toHaveBeenCalledWith('token', 42)
  })

  it('открывает и закрывает таблицу размеров', async () => {
    const wrapper = mountPage()
    await flushPromises()
    await wrapper.find('.size-chart-link').trigger('click')
    expect(document.body.querySelector('.size-modal')).not.toBeNull()
    document.body.querySelector('.size-modal__close').click()
    await wrapper.vm.$nextTick()
    expect(document.body.querySelector('.size-modal')).toBeNull()
  })

  it('удаляет позицию при уменьшении количества до нуля', async () => {
    mocks.shop.cart = { items: [{ cart_item_id: 8, variant_id: 11, quantity: 1 }] }
    const wrapper = mountPage()
    await flushPromises()
    await wrapper.findAll('.qty-btn')[0].trigger('click')
    expect(mocks.shop.RemoveFromCart).toHaveBeenCalledWith('token', 8)
  })

  it('управляет полноэкранной галереей стрелками, клавиатурой и свайпом', async () => {
    const wrapper = mountPage()
    await flushPromises()
    await wrapper.find('.gallery-zoom-btn').trigger('click')
    document.body.querySelector('.fullscreen-arrow--next').click()
    await wrapper.vm.$nextTick()
    expect(document.body.querySelector('.fullscreen-counter').textContent).toContain('2 / 2')
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowLeft' }))
    await wrapper.vm.$nextTick()
    expect(document.body.querySelector('.fullscreen-counter').textContent).toContain('1 / 2')
    const modal = document.body.querySelector('.fullscreen-gallery-modal')
    modal.dispatchEvent(new MouseEvent('mousedown', { clientX: 100, clientY: 10, bubbles: true }))
    modal.dispatchEvent(new MouseEvent('mouseup', { clientX: 20, clientY: 12, bubbles: true }))
    await wrapper.vm.$nextTick()
    expect(document.body.querySelector('.fullscreen-counter').textContent).toContain('2 / 2')
  })
})
