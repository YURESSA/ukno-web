import { beforeEach, describe, expect, it, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

const mocks = vi.hoisted(() => ({
  router: { push: vi.fn() },
  data: { auth_key: null },
  shop: { favorites: [], FetchFavorites: vi.fn(), ToggleFavorite: vi.fn() },
}))
vi.mock('vue-router', () => ({ useRouter: () => mocks.router }))
vi.mock('@/stores/counter', () => ({ useDataStore: () => mocks.data }))
vi.mock('@/stores/shop', () => ({ useShopStore: () => mocks.shop }))

import FavoritePage from '@/pages/shop/favorite/FavoritePage.vue'

const mountPage = () => shallowMount(FavoritePage, {
  global: { stubs: { RouterLink: true, ProductCard: true } },
})

describe('FavoritePage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.data.auth_key = null
    mocks.shop.favorites = []
    mocks.shop.FetchFavorites.mockResolvedValue()
  })

  it('не запрашивает избранное для гостя и показывает приглашение войти', () => {
    const wrapper = mountPage()
    expect(mocks.shop.FetchFavorites).not.toHaveBeenCalled()
    expect(wrapper.find('.auth-prompt').exists()).toBe(true)
  })

  it('загружает и отображает избранное пользователя', async () => {
    mocks.data.auth_key = 'token'
    mocks.shop.favorites = [{ product: { product_id: 4, name: 'Bag' } }]
    const wrapper = mountPage()
    await Promise.resolve()
    expect(mocks.shop.FetchFavorites).toHaveBeenCalledWith('token')
    expect(wrapper.findComponent({ name: 'ProductCard' }).exists()).toBe(true)
  })

  it('обрабатывает переход к товару и удаление из избранного', async () => {
    mocks.data.auth_key = 'token'
    mocks.shop.favorites = [{ product: { product_id: 4, name: 'Bag' } }]
    const wrapper = mountPage()
    const card = wrapper.findComponent({ name: 'ProductCard' })
    await card.vm.$emit('click')
    await card.vm.$emit('favorite')
    expect(mocks.router.push).toHaveBeenCalledWith('/shop/4')
    expect(mocks.shop.ToggleFavorite).toHaveBeenCalledWith('token', 4)
  })
})
