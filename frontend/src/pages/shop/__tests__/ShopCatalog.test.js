import { beforeEach, describe, expect, it, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

const mocks = vi.hoisted(() => ({
  router: { push: vi.fn() },
  data: { auth_key: null },
  shop: {
    banners: [], categories: [], products: [], loading: false,
    FetchHome: vi.fn(), FetchProducts: vi.fn(), ToggleFavorite: vi.fn(),
  },
}))

vi.mock('vue-router', () => ({ useRouter: () => mocks.router }))
vi.mock('@/stores/counter', () => ({
  baseUrl: 'http://localhost:8000/', useDataStore: () => mocks.data,
}))
vi.mock('@/stores/shop', () => ({ useShopStore: () => mocks.shop }))

import ShopCatalog from '@/pages/shop/catalog/ShopCatalog.vue'
import ProductCard from '@/components/shop/ProductCard.vue'

const mountPage = () => shallowMount(ShopCatalog, {
  global: { stubs: { ProductCard: { template: '<button class="product-stub" @click="$emit(\'click\')" />', props: ['product'] } } },
})

describe('ShopCatalog', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    Object.assign(mocks.shop, { banners: [], categories: [], products: [], loading: false })
    mocks.data.auth_key = null
    mocks.shop.FetchHome.mockResolvedValue()
    mocks.shop.FetchProducts.mockResolvedValue()
  })

  it('загружает главную магазина при монтировании', async () => {
    mountPage()
    await vi.runAllTimersAsync()
    expect(mocks.shop.FetchHome).toHaveBeenCalledOnce()
  })

  it('фильтрует каталог по категории и поиску', async () => {
    mocks.shop.categories = [{ category_id: 3, name: 'Худи' }]
    const wrapper = mountPage()
    await wrapper.findAll('.filter-btn')[1].trigger('click')
    await wrapper.find('.search-input').setValue('  black  ')
    await vi.advanceTimersByTimeAsync(350)
    expect(mocks.shop.FetchProducts).toHaveBeenLastCalledWith(3, 'black')
  })

  it('очищает поиск и сбрасывает фильтры', async () => {
    mocks.shop.categories = [{ category_id: 3, name: 'Худи' }]
    const wrapper = mountPage()
    await wrapper.findAll('.filter-btn')[1].trigger('click')
    await wrapper.find('.search-input').setValue('hoodie')
    await wrapper.find('.search-clear').trigger('click')
    expect(mocks.shop.FetchProducts).toHaveBeenLastCalledWith(3, null)
  })

  it('переключает баннеры по стрелкам и свайпу', async () => {
    mocks.shop.banners = [{ banner_id: 1 }, { banner_id: 2 }]
    const wrapper = mountPage()
    await wrapper.find('.hero-arrow--next').trigger('click')
    expect(wrapper.find('.hero-track').attributes('style')).toContain('-100%')
    await wrapper.find('.hero-section').trigger('mousedown', { clientX: 100, clientY: 10 })
    await wrapper.find('.hero-section').trigger('mouseup', { clientX: 180, clientY: 12 })
    expect(wrapper.find('.hero-track').attributes('style')).toContain('-0%')
  })

  it('ведёт гостя на login при добавлении в избранное', async () => {
    mocks.shop.products = [{ product_id: 7, name: 'Cap' }]
    const wrapper = mountPage()
    await wrapper.findComponent(ProductCard).vm.$emit('favorite')
    expect(mocks.router.push).toHaveBeenCalledWith('/login')
    expect(mocks.shop.ToggleFavorite).not.toHaveBeenCalled()
  })

  it('открывает товар и переключает избранное авторизованному пользователю', async () => {
    mocks.data.auth_key = 'token'
    mocks.shop.products = [{ product_id: 7, name: 'Cap' }]
    const wrapper = mountPage()
    const card = wrapper.findComponent(ProductCard)
    await card.vm.$emit('click')
    await card.vm.$emit('favorite')
    expect(mocks.router.push).toHaveBeenCalledWith('/shop/7')
    expect(mocks.shop.ToggleFavorite).toHaveBeenCalledWith('token', 7)
  })
})
