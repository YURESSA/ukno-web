import { test, expect } from '@playwright/test'

function randomUser() {
  const rand = Math.floor(Math.random() * 90000) + 10000
  return {
    email: `journey_user_${rand}@ukno.test`,
    password: 'Password123!',
    token: `mock_jwt_token_${rand}`,
    role: 'user',
  }
}

const MOCK_PRODUCT = {
  product_id: 101,
  name: 'Фирменное худи UKNO «Архитектура»',
  category_id: 1,
  category_name: 'Одежда',
  description: 'Плотный хлопок 350 г/м², вышивка логотипа на груди.',
  price: 4500,
  main_image: 'logo/logo-with-text.svg',
  is_active: true,
  colors: [
    {
      color_id: 1,
      name: 'Чёрный',
      hex_code: '#000000',
      images: [{ image_id: 1, image_path: 'logo/logo-with-text.svg', is_main: true }],
      sizes: [
        { variant_id: 10, size_id: 1, size_name: 'M', stock: 15 },
        { variant_id: 11, size_id: 2, size_name: 'L', stock: 5 },
      ],
    },
  ],
}

const MOCK_HOME = {
  banners: [
    {
      banner_id: 1,
      title: 'Новая коллекция мерча UKNO',
      description: 'Архитектурный мерч для резидентов и гостей',
      button_text: 'В каталог',
      image_path: 'logo/logo-with-text.svg',
    },
  ],
  categories: [
    { category_id: 1, name: 'Одежда' },
    { category_id: 2, name: 'Аксессуары' },
  ],
  products: [MOCK_PRODUCT],
}

async function mockJourneyAPI(page, user) {
  let cartItems = []
  let ordersList = []
  let favoriteIds = []

  function getCart() {
    const total = cartItems.reduce((acc, it) => acc + Number(it.subtotal || 0), 0)
    return { items: cartItems, total_price: String(total) }
  }

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
      body: JSON.stringify({
        email: user.email,
        role: user.role,
        name: 'Иван',
        full_name: 'Иванов Иван Иванович',
      }),
    }),
  )

  await page.route((url) => url.pathname.endsWith('/api/user/merch'), (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_HOME) }),
  )

  await page.route((url) => url.pathname.endsWith('/api/user/merch/products'), (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ products: MOCK_HOME.products }) }),
  )

  await page.route((url) => /\/api\/user\/merch\/products\/\d+$/.test(url.pathname), (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_PRODUCT) }),
  )

  await page.route((url) => url.pathname.endsWith('/api/user/merch/favorites'), (route) => {
    const favProducts = favoriteIds.map((id) => {
      const prod = id === 101 ? MOCK_PRODUCT : null
      return prod ? { favorite_id: id, product: prod, added_at: '2026-07-27T12:00:00Z' } : null
    }).filter(Boolean)
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ favorites: favProducts }) })
  })

  await page.route((url) => /\/api\/user\/merch\/products\/(\d+)\/favorite$/.test(url.pathname), (route) => {
    const idMatch = route.request().url().match(/\/products\/(\d+)\/favorite/)
    const prodId = idMatch ? Number(idMatch[1]) : 101
    const idx = favoriteIds.indexOf(prodId)
    let is_fav = true
    if (idx >= 0) {
      favoriteIds.splice(idx, 1)
      is_fav = false
    } else {
      favoriteIds.push(prodId)
      is_fav = true
    }
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ is_favorite: is_fav }) })
  })

  await page.route(
    (url) => url.pathname.endsWith('/api/user/merch/cart') && !url.pathname.includes('/cart/'),
    async (route) => {
      const method = route.request().method()
      if (method === 'GET') {
        route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(getCart()) })
      } else if (method === 'POST') {
        const body = JSON.parse(route.request().postData() || '{}')
        const qty = body.quantity || 1
        const price = MOCK_PRODUCT.price
        cartItems.push({
          cart_item_id: cartItems.length + 1,
          variant_id: body.variant_id || 10,
          quantity: qty,
          subtotal: String(qty * price),
          available: 15,
          product: MOCK_PRODUCT,
          color: MOCK_PRODUCT.colors[0],
          size: MOCK_PRODUCT.colors[0].sizes[0],
        })
        route.fulfill({ status: 201, contentType: 'application/json', body: JSON.stringify({ success: true }) })
      } else {
        route.continue()
      }
    },
  )

  await page.route(
    (url) => /\/api\/user\/merch\/cart\/\d+$/.test(url.pathname),
    async (route) => {
      const method = route.request().method()
      const idMatch = route.request().url().match(/\/cart\/(\d+)/)
      const cartItemId = idMatch ? Number(idMatch[1]) : 1
      if (method === 'PUT') {
        const body = JSON.parse(route.request().postData() || '{}')
        const item = cartItems.find((i) => i.cart_item_id === cartItemId)
        if (item) {
          item.quantity = body.quantity || 1
          item.subtotal = String(item.quantity * Number(item.product.price))
        }
        route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true }) })
      } else if (method === 'DELETE') {
        cartItems = cartItems.filter((i) => i.cart_item_id !== cartItemId)
        route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true }) })
      } else {
        route.continue()
      }
    },
  )

  await page.route(
    (url) => url.pathname.endsWith('/api/user/merch/orders'),
    async (route) => {
      const method = route.request().method()
      if (method === 'GET') {
        route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ orders: ordersList }) })
      } else if (method === 'POST') {
        const orderData = JSON.parse(route.request().postData() || '{}')
        const cartState = getCart()
        const newOrder = {
          order_id: 501,
          status: 'awaiting_payment',
          total_price: cartState.total_price,
          created_at: new Date().toISOString(),
          delivery_method: orderData.delivery_method || 'pickup',
          pay_by_card: orderData.pay_by_card ?? true,
          items: cartItems.map((ci) => ({
            order_item_id: ci.cart_item_id,
            product_id: ci.product.product_id,
            product_name: ci.product.name,
            quantity: ci.quantity,
            price: ci.product.price,
            subtotal: ci.subtotal,
          })),
        }
        ordersList.unshift(newOrder)
        cartItems = []
        route.fulfill({ status: 201, contentType: 'application/json', body: JSON.stringify({ success: true, order: newOrder }) })
      } else {
        route.continue()
      }
    },
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

test.describe('E2E Customer Journeys — Магазин UKNO', () => {
  test('Сценарий 1: Полный путь покупки товара — от каталога до оформления заказа', async ({ page }) => {
    const user = randomUser()
    await mockJourneyAPI(page, user)

    await loginAs(page, user)

    await page.goto('/shop')
    await page.waitForSelector('.product-card', { timeout: 10_000 })

    const firstCard = page.locator('.product-card').first()
    await expect(firstCard).toContainText('Фирменное худи UKNO «Архитектура»')
    await firstCard.click()

    await page.waitForURL((url) => url.pathname.includes('/shop/101'), { timeout: 5_000 })
    const addBtn = page.locator('.product-add-btn')
    await expect(addBtn).toBeVisible()
    await expect(addBtn).toBeEnabled()
    await addBtn.click()

    await expect(page.locator('.added-message')).toBeVisible({ timeout: 5_000 })

    await page.goto('/shop/orders')
    const cartItem = page.locator('.cart-item').first()
    await expect(cartItem).toBeVisible({ timeout: 5_000 })
    await expect(cartItem).toContainText('Фирменное худи UKNO «Архитектура»')
    await expect(cartItem.locator('.cart-item__price')).toContainText('4 500 ₽')

    const continueBtn = page.locator('.summary-continue-btn')
    await expect(continueBtn).toBeVisible()
    await continueBtn.click()

    const lastNameInput = page.locator('input[placeholder="Фамилия"]')
    const firstNameInput = page.locator('input[placeholder="Имя"]')
    await expect(lastNameInput).toHaveValue('Иванов', { timeout: 5_000 })
    await expect(firstNameInput).toHaveValue('Иван')

    const contactInput = page.locator('input[placeholder*="связаться"]')
    await contactInput.fill('+7 (999) 000-00-00')

    const submitOrderBtn = page.locator('.summary-continue-btn')
    await expect(submitOrderBtn).toBeEnabled()
    await submitOrderBtn.click()

    const orderCard = page.locator('.order-card').first()
    await expect(orderCard).toBeVisible({ timeout: 10_000 })
    await expect(orderCard).toContainText('Заказ #501')
    await expect(orderCard).toContainText('4 500 ₽')
    await expect(orderCard).toContainText('Фирменное худи UKNO «Архитектура» × 1')
  })

  test('Сценарий 2: Полный путь работы с избранным (добавление и удаление из вишлиста)', async ({ page }) => {
    const user = randomUser()
    await mockJourneyAPI(page, user)

    await loginAs(page, user)

    await page.goto('/shop')
    await page.waitForSelector('.product-card', { timeout: 10_000 })

    const favBtn = page.locator('.product-card__fav').first()
    await expect(favBtn).toBeVisible()
    await favBtn.click()

    await page.goto('/shop/favorite')
    const favCard = page.locator('.product-card').first()
    await expect(favCard).toBeVisible({ timeout: 5_000 })
    await expect(favCard).toContainText('Фирменное худи UKNO «Архитектура»')

    const removeFavBtn = favCard.locator('.product-card__fav')
    await removeFavBtn.click()

    const emptyState = page.locator('.empty-state')
    await expect(emptyState).toBeVisible({ timeout: 5_000 })
    await expect(emptyState).toContainText('Вы ещё ничего не добавили в избранное')
  })
})
