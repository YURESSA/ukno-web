import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref } from 'vue'

const mocks = vi.hoisted(() => ({
  store: { auth_key: 'admin-token' },
  message: { success: vi.fn(), error: vi.fn(), warning: vi.fn() },
  dialog: { warning: vi.fn() },
}))

vi.mock('axios')
vi.mock('@/stores/counter', () => ({ baseUrl: 'http://localhost:8000/', useDataStore: () => mocks.store }))
vi.mock('naive-ui', () => {
  const stub = { template: '<div><slot /></div>' }
  return {
    NTabs: stub, NTabPane: stub, NDataTable: stub, NModal: stub, NForm: stub,
    NFormItemGi: stub, NGrid: stub, NInput: stub, NInputNumber: stub, NSelect: stub,
    NSwitch: stub, NColorPicker: stub, NButton: stub, NSpace: stub, NAvatar: stub,
    NUpload: stub, NUploadDragger: stub, NIcon: stub, NTag: stub, NDescriptions: stub,
    NDescriptionsItem: stub, NDivider: stub,
    useMessage: () => mocks.message, useDialog: () => mocks.dialog,
  }
})

import axios from 'axios'
import MerchSection from '@/pages/adminPanel/sections/MerchSection.vue'

function defaultGet(url) {
  if (url.endsWith('/products')) return Promise.resolve({ data: { products: [] } })
  if (url.endsWith('/categories')) return Promise.resolve({ data: { categories: [] } })
  if (url.endsWith('/banners')) return Promise.resolve({ data: { banners: [] } })
  if (url.endsWith('/orders')) return Promise.resolve({ data: { orders: [] } })
  return Promise.resolve({ data: {} })
}

const mountSection = () => mount(MerchSection, {
  global: { provide: { 'admin-add-event': ref(0) }, stubs: { Teleport: true } },
})

describe('MerchSection', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    axios.get.mockImplementation(defaultGet)
    axios.post.mockResolvedValue({ data: {} })
    axios.put.mockResolvedValue({ data: {} })
    axios.patch.mockResolvedValue({ data: {} })
    axios.delete.mockResolvedValue({ data: {} })
  })

  it('загружает товары, категории, баннеры и заказы администратора', async () => {
    mountSection()
    await vi.waitFor(() => expect(axios.get).toHaveBeenCalledTimes(4))
    for (const endpoint of ['products', 'categories', 'banners', 'orders']) {
      expect(axios.get).toHaveBeenCalledWith(
        `http://localhost:8000/api/admin/merch/${endpoint}`,
        { headers: { Authorization: 'Bearer admin-token' } },
      )
    }
  })

  it('открывает создание товара и управляет цветами и размерами', async () => {
    const wrapper = mountSection()
    await vi.waitFor(() => expect(axios.get).toHaveBeenCalledTimes(4))
    wrapper.vm.openCreateProduct()
    wrapper.vm.addColor()
    wrapper.vm.addSize(0)
    expect(wrapper.vm.productForm.colors).toHaveLength(1)
    expect(wrapper.vm.productForm.colors[0].sizes).toHaveLength(1)
    wrapper.vm.removeSize(0, 0)
    wrapper.vm.removeColor(0)
    expect(wrapper.vm.productForm.colors).toEqual([])
  })

  it('валидирует название товара перед сохранением', async () => {
    const wrapper = mountSection()
    await vi.waitFor(() => expect(axios.get).toHaveBeenCalledTimes(4))
    wrapper.vm.openCreateProduct()
    await wrapper.vm.saveProduct()
    expect(mocks.message.warning).toHaveBeenCalled()
    expect(axios.post).not.toHaveBeenCalled()
  })

  it('создаёт товар multipart-запросом и обновляет список', async () => {
    const wrapper = mountSection()
    await vi.waitFor(() => expect(axios.get).toHaveBeenCalledTimes(4))
    wrapper.vm.openCreateProduct()
    wrapper.vm.productForm.name = 'Cap'
    wrapper.vm.productForm.price = 1500
    await wrapper.vm.saveProduct()
    expect(axios.post).toHaveBeenCalledWith(
      'http://localhost:8000/api/admin/merch/products',
      expect.any(FormData),
      { headers: { Authorization: 'Bearer admin-token', 'Content-Type': 'multipart/form-data' } },
    )
    expect(mocks.message.success).toHaveBeenCalled()
  })

  it('загружает полную карточку товара для редактирования', async () => {
    axios.get.mockImplementation((url) => {
      if (url.endsWith('/products/5')) return Promise.resolve({ data: {
        product_id: 5, name: 'Hoodie', price: '3000', category: { category_id: 2 },
        colors: [{ color_id: 1, name: 'Black', sizes: [{ variant_id: 7, size: { name: 'M' }, stock: 2 }] }],
        images: [{ image_id: 9, image_path: 'hoodie.jpg' }],
      } })
      return defaultGet(url)
    })
    const wrapper = mountSection()
    await vi.waitFor(() => expect(axios.get).toHaveBeenCalledTimes(4))
    await wrapper.vm.openEditProduct({ product_id: 5 })
    expect(wrapper.vm.productForm.name).toBe('Hoodie')
    expect(wrapper.vm.productForm.colors[0].sizes[0].size_name).toBe('M')
    expect(wrapper.vm.productFileList[0].id).toBe('old-9')
  })

  it('обновляет статус выбранного заказа', async () => {
    const wrapper = mountSection()
    await vi.waitFor(() => expect(axios.get).toHaveBeenCalledTimes(4))
    wrapper.vm.openOrderModal({ order_id: 12, status: 'new', delivery_method: 'pickup', pay_by_card: false })
    wrapper.vm.selectedOrderStatus = 'completed'
    await wrapper.vm.saveOrderStatus()
    expect(axios.patch).toHaveBeenCalledWith(
      'http://localhost:8000/api/admin/merch/orders/12',
      { status: 'completed' },
      { headers: { Authorization: 'Bearer admin-token' } },
    )
  })

  it('возвращает допустимые статусы для способов оплаты и доставки', async () => {
    const wrapper = mountSection()
    await vi.waitFor(() => expect(axios.get).toHaveBeenCalledTimes(4))
    expect(wrapper.vm.getOrderStatusOptions({ delivery_method: 'delivery' })).toHaveLength(4)
    expect(wrapper.vm.getOrderStatusOptions({ delivery_method: 'pickup', pay_by_card: true }).map(x => x.value)).toContain('paid')
    expect(wrapper.vm.getOrderStatusOptions({ delivery_method: 'pickup', pay_by_card: false }).map(x => x.value)).toEqual(['new', 'completed', 'cancelled'])
  })

  it('создаёт и обновляет категории', async () => {
    const wrapper = mountSection()
    await vi.waitFor(() => expect(axios.get).toHaveBeenCalledTimes(4))
    wrapper.vm.categoryForm.name = 'Hoodies'
    await wrapper.vm.saveCategory()
    expect(axios.post).toHaveBeenCalledWith(
      'http://localhost:8000/api/admin/merch/categories', expect.objectContaining({ name: 'Hoodies' }),
      { headers: { Authorization: 'Bearer admin-token' } },
    )
    wrapper.vm.isEdit = true
    wrapper.vm.categoryForm.category_id = 3
    await wrapper.vm.saveCategory()
    expect(axios.put).toHaveBeenCalledWith(
      'http://localhost:8000/api/admin/merch/categories/3', expect.any(Object),
      { headers: { Authorization: 'Bearer admin-token' } },
    )
  })

  it('создаёт и обновляет баннеры', async () => {
    const wrapper = mountSection()
    await vi.waitFor(() => expect(axios.get).toHaveBeenCalledTimes(4))
    wrapper.vm.bannerForm.title = 'Drop'
    await wrapper.vm.saveBanner()
    expect(axios.post).toHaveBeenCalledWith(
      'http://localhost:8000/api/admin/merch/banners', expect.any(FormData), expect.any(Object),
    )
    wrapper.vm.isEdit = true
    wrapper.vm.bannerForm.banner_id = 6
    await wrapper.vm.saveBanner()
    expect(axios.put).toHaveBeenCalledWith(
      'http://localhost:8000/api/admin/merch/banners/6', expect.any(FormData), expect.any(Object),
    )
  })

  it('обрабатывает новые файлы товара и баннера', async () => {
    const wrapper = mountSection()
    await vi.waitFor(() => expect(axios.get).toHaveBeenCalledTimes(4))
    const file = new File(['image'], 'image.jpg', { type: 'image/jpeg' })
    wrapper.vm.handleProductUploadChange({ fileList: [{ name: 'image.jpg', file }] })
    expect(wrapper.vm.newProductFiles).toEqual([file])
    expect(await wrapper.vm.handleProductRemove({ file: { id: 'new-1', name: 'image.jpg' } })).toBe(true)
    wrapper.vm.handleBannerUploadChange({ fileList: [{ file }] })
    expect(wrapper.vm.newBannerFile).toBe(file)
  })

  it('подтверждает удаление товара, категории и баннера', async () => {
    const wrapper = mountSection()
    await vi.waitFor(() => expect(axios.get).toHaveBeenCalledTimes(4))
    wrapper.vm.productForm = { product_id: 2, name: 'Cap' }
    wrapper.vm.confirmDeleteProduct()
    await mocks.dialog.warning.mock.calls.at(-1)[0].onPositiveClick()
    expect(axios.delete).toHaveBeenCalledWith('http://localhost:8000/api/admin/merch/products/2', expect.any(Object))
    wrapper.vm.categoryForm = { category_id: 3 }
    wrapper.vm.confirmDeleteCategory()
    await mocks.dialog.warning.mock.calls.at(-1)[0].onPositiveClick()
    wrapper.vm.bannerForm = { banner_id: 4 }
    wrapper.vm.confirmDeleteBanner()
    await mocks.dialog.warning.mock.calls.at(-1)[0].onPositiveClick()
    expect(axios.delete).toHaveBeenCalledWith('http://localhost:8000/api/admin/merch/categories/3', expect.any(Object))
    expect(axios.delete).toHaveBeenCalledWith('http://localhost:8000/api/admin/merch/banners/4', expect.any(Object))
  })

  it('сообщает об ошибках загрузки и сохранения', async () => {
    const wrapper = mountSection()
    await vi.waitFor(() => expect(axios.get).toHaveBeenCalledTimes(4))
    axios.get.mockRejectedValueOnce({ response: { data: { message: 'Load failed' } } })
    await wrapper.vm.openEditProduct({ product_id: 99 })
    expect(mocks.message.error).toHaveBeenCalledWith('Load failed')
    axios.post.mockRejectedValueOnce({ response: { data: { message: 'Save failed' } } })
    wrapper.vm.openCreateProduct()
    wrapper.vm.productForm.name = 'Cap'
    await wrapper.vm.saveProduct()
    expect(mocks.message.error).toHaveBeenCalledWith('Save failed')
  })
})
