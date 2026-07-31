import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'

const mocks = vi.hoisted(() => ({
  route: { name: 'ShopCatalog', path: '/shop' },
  data: { auth_key: null, role: null },
  shop: {
    cart: { items: [], total_price: '0' }, favorites: [], cartItemsCount: 0, favoritesCount: 0,
    FetchCart: vi.fn(), FetchFavorites: vi.fn(),
  },
}))
vi.mock('vue-router', () => ({ useRoute: () => mocks.route }))
vi.mock('@/stores/counter', () => ({ useDataStore: () => mocks.data }))
vi.mock('@/stores/shop', () => ({ useShopStore: () => mocks.shop }))
vi.mock('@/components/shared', () => ({ SFooter: { template: '<footer />' } }))

import ShopLayout from '@/layouts/ShopLayout.vue'

const mountLayout = () => mount(ShopLayout, {
  global: { stubs: { RouterLink: { template: '<a><slot /></a>' }, RouterView: true } },
})

describe('ShopLayout', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    Object.assign(mocks.data, { auth_key: null, role: null })
    Object.assign(mocks.shop, {
      cart: { items: [], total_price: '0' }, favorites: [], cartItemsCount: 0, favoritesCount: 0,
    })
  })

  it('показывает вход гостю и не загружает приватные данные', () => {
    const wrapper = mountLayout()
    expect(wrapper.find('.shop-auth-btn').exists()).toBe(true)
    expect(mocks.shop.FetchCart).not.toHaveBeenCalled()
  })

  it('загружает корзину и избранное авторизованного пользователя', async () => {
    mocks.data.auth_key = 'token'
    mocks.shop.cartItemsCount = 3
    mocks.shop.favoritesCount = 2
    const wrapper = mountLayout()
    await Promise.resolve()
    expect(mocks.shop.FetchCart).toHaveBeenCalledWith('token')
    expect(mocks.shop.FetchFavorites).toHaveBeenCalledWith('token')
    expect(wrapper.find('.shop-cart-count').text()).toBe('3')
    expect(wrapper.find('.shop-nav-badge').text()).toBe('2')
  })
})
