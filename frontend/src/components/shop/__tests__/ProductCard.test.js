import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'

vi.mock('axios')
vi.mock('@/stores/counter', () => ({
  baseUrl: 'http://localhost:8000/',
}))

import ProductCard from '@/components/shop/ProductCard.vue'
import { useShopStore } from '@/stores/shop'

const makeProduct = (overrides = {}) => ({
  product_id: 42,
  name: 'Тестовая Футболка UKNO',
  price: '2500.00',
  main_image: '/media/products/shirt.jpg',
  images: [
    { image_path: '/media/products/shirt_2.jpg' },
  ],
  is_favorite: false,
  available: 1,
  ...overrides,
})

function mountCard(productOverrides = {}, storeState = {}) {
  const pinia = createTestingPinia({
    createSpy: vi.fn,
    initialState: {
      shop: {
        favorites: [],
        ...storeState,
      },
    },
  })

  return mount(ProductCard, {
    global: {
      plugins: [pinia],
      stubs: { RouterLink: true, RouterView: true },
    },
    props: {
      product: makeProduct(productOverrides),
    },
  })
}

describe('ProductCard — рендер содержимого', () => {

  it('отображает название товара в .product-card__name', () => {
    const wrapper = mountCard({ name: 'Лимитированная Кружка' })
    expect(wrapper.find('.product-card__name').text()).toBe('Лимитированная Кружка')
  })

  it('отображает отформатированную цену в .product-card__price', () => {
    const wrapper = mountCard({ price: '2500.00' })
    const priceText = wrapper.find('.product-card__price').text()
    expect(priceText).toContain('₽')
    expect(priceText).toContain('2')
  })

  it('рендерит изображение товара, когда main_image задан', () => {
    const wrapper = mountCard({
      main_image: '/media/test.jpg',
      images: [],
    })

    expect(wrapper.find('.product-card__slides').exists()).toBe(true)
    expect(wrapper.find('.product-card__img-placeholder').exists()).toBe(false)
  })

  it('рендерит SVG-плейсхолдер в .product-card__img-placeholder, если изображений нет', () => {
    const wrapper = mountCard({
      main_image: null,
      images: [],
    })

    const placeholder = wrapper.find('.product-card__img-placeholder')
    expect(placeholder.exists()).toBe(true)

    const svg = placeholder.find('svg')
    expect(svg.exists()).toBe(true)
  })
})

describe('ProductCard — события click и favorite', () => {

  it('эмитит событие "click" при клике на карточку (.product-card)', async () => {
    const wrapper = mountCard()
    await wrapper.find('.product-card').trigger('click')

    expect(wrapper.emitted('click')).toBeTruthy()
    expect(wrapper.emitted('click')).toHaveLength(1)
  })

  it('эмитит событие "favorite" при клике на кнопку .product-card__fav', async () => {
    const wrapper = mountCard()
    await wrapper.find('.product-card__fav').trigger('click')

    expect(wrapper.emitted('favorite')).toBeTruthy()
    expect(wrapper.emitted('favorite')).toHaveLength(1)
  })

  it('клик на кнопку избранного НЕ эмитит событие "click" (модификатор .stop)', async () => {
    const wrapper = mountCard()
    await wrapper.find('.product-card__fav').trigger('click')

    expect(wrapper.emitted('favorite')).toHaveLength(1)
    expect(wrapper.emitted('click')).toBeFalsy()
  })
})

describe('ProductCard — состояние избранного', () => {
  it('кнопка .product-card__fav имеет класс .active, если товар в избранном', () => {
    const wrapper = mountCard({ is_favorite: true })
    const favBtn = wrapper.find('.product-card__fav')

    expect(favBtn.classes()).toContain('active')
  })

  it('кнопка .product-card__fav НЕ имеет класс .active, если товар не в избранном', () => {
    const wrapper = mountCard({ is_favorite: false, product_id: 999 })
    const favBtn = wrapper.find('.product-card__fav')

    expect(favBtn.classes()).not.toContain('active')
  })

  it('кнопка избранного активна, если product_id есть в favoriteProductIds стора', () => {
    const wrapper = mountCard(
      { product_id: 77, is_favorite: false },
      { favorites: [{ id: 1, product: { product_id: 77 } }] },
    )

    const favBtn = wrapper.find('.product-card__fav')
    expect(favBtn.classes()).toContain('active')
  })
})

describe('ProductCard — доступность товара', () => {

  it('показывает бейдж "Нет в наличии", если available === 0', () => {
    const wrapper = mountCard({ available: 0 })
    const badge = wrapper.find('.out-of-stock')

    expect(badge.exists()).toBe(true)
    expect(badge.text()).toContain('Нет в наличии')
  })

  it('НЕ показывает бейдж "Нет в наличии", если товар в наличии', () => {
    const wrapper = mountCard({ available: 5 })
    expect(wrapper.find('.out-of-stock').exists()).toBe(false)
  })
})
