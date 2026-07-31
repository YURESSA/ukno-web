import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'

const mocks = vi.hoisted(() => ({
  data: { auth_key: null, profileData: null, GetProfile: vi.fn() },
  shop: {
    cart: { items: [], total_price: '0' }, orders: [], loading: false, cartLoading: false,
    cartItemsCount: 0, favoriteProductIds: [], FetchCart: vi.fn(), FetchOrders: vi.fn(),
    UpdateCartItem: vi.fn(), RemoveFromCart: vi.fn(), ToggleFavorite: vi.fn(), CreateOrder: vi.fn(),
  },
}))
vi.mock('@/stores/counter', () => ({ baseUrl: '/api/', useDataStore: () => mocks.data }))
vi.mock('@/stores/shop', () => ({ useShopStore: () => mocks.shop }))

import OrdersPage from '@/pages/shop/orders/OrdersPage.vue'

const mountPage = () => mount(OrdersPage, { global: { stubs: { RouterLink: true } } })

describe('OrdersPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    Object.assign(mocks.data, { auth_key: null, profileData: null })
    Object.assign(mocks.shop, {
      cart: { items: [], total_price: '0' }, orders: [], loading: false, cartLoading: false,
      cartItemsCount: 0, favoriteProductIds: [],
    })
    for (const method of ['FetchCart', 'FetchOrders', 'UpdateCartItem', 'RemoveFromCart', 'ToggleFavorite', 'CreateOrder']) {
      mocks.shop[method].mockResolvedValue()
    }
  })

  it('показывает приглашение войти гостю', () => {
    expect(mountPage().find('.auth-prompt').exists()).toBe(true)
    expect(mocks.shop.FetchCart).not.toHaveBeenCalled()
  })

  it('загружает корзину и заполняет ФИО из профиля', async () => {
    mocks.data.auth_key = 'token'
    mocks.data.profileData = { full_name: 'Иванов Иван Иванович' }
    mocks.shop.cart = { items: [{ cart_item_id: 1, quantity: 1, available: 3, subtotal: '2500', product: { product_id: 2, name: 'Cap' } }], total_price: '2500' }
    const wrapper = mountPage()
    await Promise.resolve()
    expect(mocks.shop.FetchCart).toHaveBeenCalledWith('token')
    await wrapper.find('.summary-continue-btn').trigger('click')
    const inputs = wrapper.findAll('.checkout-input')
    expect(inputs[0].element.value).toBe('Иванов')
    expect(inputs[1].element.value).toBe('Иван')
  })

  it('обновляет количество, удаляет товар и переключает избранное', async () => {
    mocks.data.auth_key = 'token'
    mocks.shop.cart = { items: [{ cart_item_id: 1, quantity: 1, available: 3, subtotal: '2500', product: { product_id: 2, name: 'Cap' } }], total_price: '2500' }
    const wrapper = mountPage()
    await Promise.resolve()
    await wrapper.findAll('.qty-btn')[1].trigger('click')
    await wrapper.find('.delete').trigger('click')
    await wrapper.find('.cart-item__action-btn:not(.delete)').trigger('click')
    expect(mocks.shop.UpdateCartItem).toHaveBeenCalledWith('token', 1, 2)
    expect(mocks.shop.RemoveFromCart).toHaveBeenCalledWith('token', 1)
    expect(mocks.shop.ToggleFavorite).toHaveBeenCalledWith('token', 2)
  })

  it('валидирует форму и оформляет заказ', async () => {
    mocks.data.auth_key = 'token'
    mocks.shop.cart = { items: [{ cart_item_id: 1, quantity: 1, available: 3, subtotal: '2500', product: { product_id: 2, name: 'Cap' } }], total_price: '2500' }
    const wrapper = mountPage()
    await Promise.resolve()
    await wrapper.find('.summary-continue-btn').trigger('click')
    const inputs = wrapper.findAll('.checkout-input')
    await inputs[0].setValue('Иванов')
    await inputs[1].setValue('Иван')
    await inputs[3].setValue('@ivan')
    await wrapper.find('.summary-continue-btn').trigger('click')
    expect(mocks.shop.CreateOrder).toHaveBeenCalledWith('token', expect.objectContaining({
      last_name: 'Иванов', first_name: 'Иван', contact_channel: '@ivan', delivery_method: 'pickup',
    }))
    expect(mocks.shop.FetchOrders).toHaveBeenCalledWith('token')
  })

  it('показывает серверную ошибку оформления', async () => {
    mocks.data.auth_key = 'token'
    mocks.shop.cart = { items: [{ cart_item_id: 1, quantity: 1, available: 3, subtotal: '2500', product: { product_id: 2, name: 'Cap' } }], total_price: '2500' }
    mocks.shop.CreateOrder.mockRejectedValueOnce({ response: { data: { message: 'Нет остатка' } } })
    const wrapper = mountPage()
    await Promise.resolve()
    await wrapper.find('.summary-continue-btn').trigger('click')
    const inputs = wrapper.findAll('.checkout-input')
    await inputs[0].setValue('Иванов'); await inputs[1].setValue('Иван'); await inputs[3].setValue('@ivan')
    await wrapper.find('.summary-continue-btn').trigger('click')
    expect(wrapper.find('.form-error').text()).toBe('Нет остатка')
  })

  it('загружает и отображает историю заказов', async () => {
    mocks.data.auth_key = 'token'
    mocks.shop.orders = [{ order_id: 9, status: 'paid', created_at: '2026-07-01', total_price: '2500', delivery_method: 'pickup', items: [] }]
    const wrapper = mountPage()
    await Promise.resolve()
    await wrapper.findAll('.orders-tab')[1].trigger('click')
    expect(mocks.shop.FetchOrders).toHaveBeenCalledWith('token')
    expect(wrapper.find('.order-card__id').text()).toContain('9')
  })
})
