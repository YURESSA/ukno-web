import { beforeEach, describe, expect, it, vi } from 'vitest'
import { shallowMount, flushPromises } from '@vue/test-utils'
import { ref } from 'vue'
import EventsSection from './EventsSection.vue'
import NewEvent from '@/pages/personal-accounts/_shared/newEvent.vue'

const mocks = vi.hoisted(() => ({
  error: vi.fn(), success: vi.fn(), notification: vi.fn().mockResolvedValue(), back: vi.fn(),
  store: {
    adminExcursions: { excursions: [] },
    getCategories: [{ category_id: 1, category_name: 'Категория' }],
    getFormat: [{ format_type_id: 2, format_type_name: 'Формат' }],
    getAge: [{ age_category_id: 3, age_category_name: 'Возраст' }],
    getExcursionsStats: { categories: [], format_types: [], age_categories: [] },
    FetchAdminExcursion: vi.fn().mockResolvedValue(), FetchCategories: vi.fn().mockResolvedValue(),
    FetchFormat: vi.fn().mockResolvedValue(), FetchAge: vi.fn().mockResolvedValue(),
    FetchExcursionsStats: vi.fn().mockResolvedValue(),
    PostNewExcursion: vi.fn().mockResolvedValue({}), PostNewEvent: vi.fn().mockResolvedValue({}),
  },
}))
vi.mock('@/stores/counter', () => ({ useDataStore: () => mocks.store, baseUrl: '/' }))
vi.mock('@/utils/notification', () => ({ notification: mocks.notification }))
vi.mock('vue-router', () => ({ useRouter: () => ({ back: mocks.back }) }))
vi.mock('@/components/shared/MapPicker.vue', () => ({ default: { template: '<div />' } }))
vi.mock('naive-ui', async importOriginal => ({
  ...await importOriginal(), useMessage: () => ({ error: mocks.error, success: mocks.success }), useDialog: () => ({}),
}))

const validEvent = () => ({
  title: 'Экскурсия', description: '<p>Описание</p>', duration: 60, place: 'Площадь',
  category_id: 1, format_type_id: 2, age_category_id: 3, is_active: true,
  sessions: [], photos: [],
})
const globalOptions = () => ({
  provide: { 'admin-add-event': ref(0) },
  renderStubDefaultSlot: true,
  stubs: {
    FormItemGridItem: { props: ['feedback'], template: '<div><slot /><span role="alert">{{ feedback }}</span></div>' },
  },
})

beforeEach(() => vi.clearAllMocks())

describe('admin event creation', () => {
  it.each([
    ['title', '', 'Введите название'], ['description', '<p><br></p>', 'Введите описание'],
    ['duration', null, 'продолжительность'], ['place', '   ', 'место проведения'],
    ['category_id', null, 'Выберите'], ['format_type_id', null, 'Выберите'], ['age_category_id', null, 'Выберите'],
  ])('blocks creation and shows field feedback for missing %s', async (key, value, message) => {
    const wrapper = shallowMount(EventsSection, { global: globalOptions() })
    wrapper.vm.selectedItem = { ...validEvent(), [key]: value }
    await wrapper.vm.handleSave()
    await flushPromises()
    expect(mocks.store.PostNewExcursion).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain(message)
    expect(wrapper.vm.activeTab).toBe(['place', 'duration'].includes(key) ? 'details' : 'main')
    wrapper.unmount()
  })

  it('sends valid multipart data; sessions and photos are optional', async () => {
    const wrapper = shallowMount(EventsSection, { global: globalOptions() })
    wrapper.vm.selectedItem = validEvent()
    await wrapper.vm.handleSave()
    const data = JSON.parse(mocks.store.PostNewExcursion.mock.calls[0][0].get('data'))
    expect(data).toMatchObject({ title: 'Экскурсия', description: '<p>Описание</p>', duration: 60, category: 'Категория', format_type: 'Формат', age_category: 'Возраст', is_active: true, sessions: [] })
    wrapper.unmount()
  })

  it('does not send a partially filled session and opens its tab', async () => {
    const wrapper = shallowMount(EventsSection, { global: globalOptions() })
    wrapper.vm.selectedItem = { ...validEvent(), sessions: [{ start_datetime: null, max_participants: 10, cost: 0 }] }
    await wrapper.vm.handleSave()
    expect(mocks.store.PostNewExcursion).not.toHaveBeenCalled()
    expect(wrapper.vm.activeTab).toBe('sessions')
    wrapper.unmount()
  })
})

describe('resident event creation', () => {
  it('shows required field errors instead of crashing on an empty date', async () => {
    const wrapper = shallowMount(NewEvent, { global: { renderStubDefaultSlot: true } })
    await wrapper.vm.submitEvent()
    await flushPromises()
    expect(mocks.store.PostNewEvent).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('Введите название события')
    expect(wrapper.text()).toContain('Выберите корректные дату и время')
    wrapper.unmount()
  })

  it('sends a valid event and preserves editable tags when a request fails', async () => {
    const wrapper = shallowMount(NewEvent, { global: { renderStubDefaultSlot: true } })
    Object.assign(wrapper.vm.formData, {
      title: 'Событие', description: 'Описание', duration: 60, place: 'Площадь',
      category: 'Категория', format_type: 'Формат', age_category: 'Возраст', tags: 'город, искусство',
      distance_to_center: '', time_to_nearest_stop: '',
    })
    wrapper.vm.formattedValue = '2030-01-01 12:00'
    mocks.store.PostNewEvent.mockRejectedValueOnce(new Error('Network Error'))
    await wrapper.vm.submitEvent()
    expect(wrapper.vm.formData.tags).toBe('город, искусство')
    expect(wrapper.vm.saving).toBe(false)
    await wrapper.vm.submitEvent()
    const data = JSON.parse(mocks.store.PostNewEvent.mock.calls[1][0].get('data'))
    expect(data).toMatchObject({
      title: 'Событие', duration: 60, is_active: true, tags: ['город', 'искусство'],
      distance_to_center: null, time_to_nearest_stop: null,
      sessions: [{ start_datetime: '2030-01-01T12:00:00', max_participants: 1, cost: 0 }],
    })
    expect(mocks.back).toHaveBeenCalledOnce()
    wrapper.unmount()
  })
})
