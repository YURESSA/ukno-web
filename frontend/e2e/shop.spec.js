import { test, expect } from '@playwright/test'

function randomUser() {
  const id = Math.random().toString(36).slice(2, 8)
  return {
    email:    `test.${id}@ukno-e2e.local`,
    password: `Pass${id}!23`,
    token:    `mock-jwt-token-${id}-${Date.now()}`,
    role:     'user',
  }
}

const MOCK_HOME = {
  banners: [
    {
      banner_id: 1,
      title: 'Новая коллекция',
      description: 'Лимитированный выпуск',
      image_path: 'media/banner1.jpg',
      button_text: 'Смотреть коллекцию',
    },
  ],
  categories: [
    { category_id: 1, name: 'Одежда' },
    { category_id: 2, name: 'Аксессуары' },
  ],
  products: [
    {
      product_id: 101,
      name: 'Худи UKNO Classic',
      price: '3500.00',
      main_image: 'media/products/hoodie.jpg',
      images: [],
      is_favorite: false,
      available: 5,
    },
    {
      product_id: 102,
      name: 'Кепка UKNO Logo',
      price: '1800.00',
      main_image: 'media/products/cap.jpg',
      images: [],
      is_favorite: false,
      available: 3,
    },
  ],
}

const MOCK_PRODUCTS_FILTERED = {
  products: [MOCK_HOME.products[0]],
}

const MOCK_PRODUCT_DETAIL = {
  product_id: 101,
  name: 'Худи UKNO Classic',
  price: '3500.00',
  description: 'Тестовое описание товара',
  main_image: 'media/products/hoodie.jpg',
  images: [],
  is_favorite: false,
  available: 5,
  colors: [
    {
      color_id: 1,
      name: 'Чёрный',
      hex_code: '#000000',
      available: 3,
      sizes: [
        { variant_id: 1, size: { name: 'M' }, stock: 3 },
        { variant_id: 2, size: { name: 'L' }, stock: 2 },
      ],
    },
  ],
}

const MOCK_CART_EMPTY    = { items: [], total_price: '0' }
const MOCK_CART_WITH_ITEM = {
  items: [{
    cart_item_id: 1,
    quantity: 1,
    product: { product_id: 101, name: 'Худи UKNO Classic', main_image: 'media/products/hoodie.jpg' },
  }],
  total_price: '3500.00',
}
const MOCK_FAVORITES = { favorites: [] }

async function mockAPI(page, user) {
  const cart = { items: MOCK_CART_EMPTY.items, total_price: MOCK_CART_EMPTY.total_price }

  await page.route('**/api/**', (route) => {
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({}) })
  })

  await page.route((url) => url.pathname.endsWith('/api/login'), (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ access_token: user.token, role: user.role }),
    }),
  )

  await page.route((url) => url.pathname.endsWith('/api/user/profile'), (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ email: user.email, role: user.role, name: 'Test User' }),
    }),
  )

  await page.route((url) => url.pathname.endsWith('/api/user/merch'), (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_HOME) }),
  )

  await page.route((url) => url.pathname.endsWith('/api/user/merch/products'), (route) => {
    const url = new URL(route.request().url())
    const response = url.searchParams.get('category_id') ? MOCK_PRODUCTS_FILTERED : { products: MOCK_HOME.products }
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(response) })
  })

  await page.route((url) => /\/api\/user\/merch\/products\/\d+$/.test(url.pathname), (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_PRODUCT_DETAIL) }),
  )

  await page.route(
    (url) => url.pathname.endsWith('/api/user/merch/cart') && !url.pathname.includes('/cart/'),
    async (route) => {
      if (route.request().method() === 'GET') {
        route.fulfill({
          status: 200, contentType: 'application/json',
          body: JSON.stringify({ items: cart.items, total_price: cart.total_price }),
        })
      } else if (route.request().method() === 'POST') {
        cart.items = MOCK_CART_WITH_ITEM.items
        cart.total_price = MOCK_CART_WITH_ITEM.total_price
        route.fulfill({ status: 201, contentType: 'application/json', body: JSON.stringify({ success: true }) })
      } else {
        route.continue()
      }
    },
  )

  await page.route((url) => url.pathname.endsWith('/api/user/merch/favorites'), (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_FAVORITES) }),
  )

  await page.route((url) => /\/api\/user\/merch\/products\/\d+\/favorite$/.test(url.pathname), (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ is_favorite: true }) }),
  )
}

async function loginAs(page, user) {
  await page.goto('/login')

  await page.fill('input[name="email"]', user.email)
  await page.fill('input[name="password"]', user.password)
  await page.click('button[type="submit"]')

  const okBtn = page.locator('.notification-wrapper button')
  await okBtn.click({ timeout: 5_000 })

  await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 5_000 })
}


test.describe('Каталог магазина — фильтрация', () => {
  test.beforeEach(async ({ page }) => {
    await mockAPI(page, randomUser())
    await page.goto('/shop')
    await page.waitForSelector('.product-card', { timeout: 10_000 })
  })

  test('Сценарий 1: Открытие каталога, выбор категории, проверка обновления товаров', async ({ page }) => {

    const cards = page.locator('.product-card')
    await expect(cards.first()).toBeVisible()
    expect(await cards.count()).toBeGreaterThan(0)

    const filterBtns = page.locator('.filter-btn')
    expect(await filterBtns.count()).toBeGreaterThanOrEqual(2)

    const categoryBtn = filterBtns.nth(1)
    await categoryBtn.click()

    await expect(categoryBtn).toHaveClass(/active/)

    await page.waitForTimeout(500)
    const hasCards = await page.locator('.product-card').count()
    const hasEmpty = await page.locator('.empty-state').count()
    expect(hasCards > 0 || hasEmpty > 0).toBe(true)

    expect(page.url()).toContain('/shop')
    expect(page.url()).not.toMatch(/\/shop\/\d+/)

    await page.screenshot({ path: 'e2e/screenshots/scenario1-filter.png' })
  })

  test('Сценарий 1.1: Поиск товара по названию через .search-input', async ({ page }) => {

    const searchInput = page.locator('.search-input')
    await expect(searchInput).toBeVisible()

    await searchInput.fill('худи')
    await page.waitForTimeout(600)

    await expect(page.locator('.search-clear')).toBeVisible()

    await searchInput.press('Enter')
    await page.waitForTimeout(500)

    const hasCards = await page.locator('.product-card').count()
    const hasEmpty = await page.locator('.empty-state').count()
    expect(hasCards > 0 || hasEmpty > 0).toBe(true)

    await page.locator('.search-clear').click()
    await page.waitForTimeout(300)
    await expect(searchInput).toHaveValue('')

    await page.screenshot({ path: 'e2e/screenshots/scenario1-search.png' })
  })
})

test.describe('Карточка товара — корзина и избранное', () => {
  test('Сценарий 2: Переход в карточку товара через клик по .product-card', async ({ page }) => {

    const user = randomUser()
    await mockAPI(page, user)
    await page.goto('/shop')
    await page.waitForSelector('.product-card', { timeout: 10_000 })

    await page.locator('.product-card').first().click()
    await page.waitForURL(/\/shop\/\d+/, { timeout: 8_000 })

    await page.waitForSelector('.product-page', { timeout: 8_000 })
    await expect(page.locator('.back-link')).toBeVisible()

    await page.screenshot({ path: 'e2e/screenshots/scenario2-product-page.png' })
  })

  test('Сценарий 2.1: Добавление товара в корзину', async ({ page }) => {

    const user = randomUser()
    await mockAPI(page, user)

    await page.goto('/')
    await loginAs(page, user)

    await page.goto('/shop/101')
    await page.waitForSelector('.product-page', { timeout: 10_000 })
    await page.waitForSelector('.product-skeleton-wrap', { state: 'hidden', timeout: 8_000 }).catch(() => {})

    const buyBtn = page.locator('.product-add-btn:not([disabled])')
    await expect(buyBtn).toBeVisible({ timeout: 8_000 })
    await expect(buyBtn).toHaveText('Купить')

    await buyBtn.click()

    const msg = page.locator('.added-message')
    await expect(msg).toBeVisible({ timeout: 5_000 })
    await expect(msg).toContainText('Добавлено в корзину')

    await page.screenshot({ path: 'e2e/screenshots/scenario2-add-to-cart.png' })
  })

  test('Сценарий 2.2: Клик на «сердечко» не вызывает навигацию (проверка @click.stop)', async ({ page }) => {
    const user = randomUser()
    await mockAPI(page, user)

    await loginAs(page, user)

    await page.goto('/shop')
    await page.waitForSelector('.product-card', { timeout: 10_000 })

    const urlBefore = page.url()

    const favBtn = page.locator('.product-card__fav').first()
    await expect(favBtn).toBeVisible()
    await favBtn.click()

    await page.waitForTimeout(800)

    expect(page.url()).not.toContain('/login')
    expect(page.url()).not.toMatch(/\/shop\/\d+/)
    expect(page.url()).toBe(urlBefore)

    await page.screenshot({ path: 'e2e/screenshots/scenario2-favorite.png' })
  })
})
