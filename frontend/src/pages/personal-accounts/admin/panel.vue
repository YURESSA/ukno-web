<template>
  <n-config-provider :theme-overrides="themeOverrides" :locale="ruRU" :date-locale="dateRuRU">
    <div class="container">
      <div class="main-header">
        <div class="title-container">
          <div class="icon">
            <RouterLink to="/">
              <img src="/logo/mobile-logo.svg" alt="">
            </RouterLink>
          </div>
          <div class="title">
            <h5>Админ панель</h5>
            <p>Управление системой</p>
          </div>
        </div>
        <div class="section-header">
          <h3>{{ currentSection }}</h3>
          <BaseButton class="add--btn" text="+ Создать запись" @click="openNewUser()" v-if="currentSection == 'Пользователи'"></BaseButton>
          <BaseButton class="add--btn" text="+ Создать запись" @click="openNewCategories()" v-if="currentSection == 'Категории'"></BaseButton>
          <BaseButton class="add--btn" text="+ Создать запись" @click="showEdit = true" v-if="currentSection == 'Типы форматов'"></BaseButton>
          <BaseButton class="add--btn" text="+ Создать запись" @click="showEdit = true" v-if="currentSection == 'Возрастные категории'"></BaseButton>
          <BaseButton class="add--btn" text="+ Создать запись" @click="openNewAdmin()" v-if="currentSection == 'События'"></BaseButton>
          <BaseButton
            v-if="currentSection === 'Новости'"
            class="add--btn"
            text="+ Создать запись"
            @click="openNewNews"
          />
          <BaseButton class="add--btn" text="+ Создать запись" @click="openNewTeam" v-if="currentSection == 'Команда'"></BaseButton>
        </div>
      </div>
      <div class="left-sidebar">
        <nav>
          <div class="nav-section">
            <BaseButton class="nav-button" :class="{ active: currentSection === 'Пользователи' }" @click="currentSection = 'Пользователи'" text="Пользователи"/>
            <BaseButton class="nav-button" :class="{ active: currentSection === 'Категории' }" @click="currentSection = 'Категории'" text="Категории"/>
            <BaseButton class="nav-button" :class="{ active: currentSection === 'Типы форматов' }" @click="currentSection = 'Типы форматов'" text="Типы форматов"/>
            <BaseButton class="nav-button" :class="{ active: currentSection === 'Возрастные категории' }" @click="currentSection = 'Возрастные категории'" text="Возрастные категории"/>
            <BaseButton class="nav-button" :class="{ active: currentSection === 'События' }" @click="currentSection = 'События'" text="События"/>
            <BaseButton class="nav-button" :class="{ active: currentSection === 'Новости' }" @click="currentSection = 'Новости'" text="Новости"/>
            <BaseButton class="nav-button" :class="{ active: currentSection === 'Брони' }" @click="currentSection = 'Брони'" text="Брони"/>
            <BaseButton class="nav-button" :class="{ active: currentSection === 'Команда' }" @click="currentSection = 'Команда'" text="Команда"/>
          </div>
        </nav>
      </div>
      <div class="main">
          <n-input
            v-model:value="search"
            clearable
            placeholder="Поиск: email, ФИО, телефон, роль..."
            style="width: 100%; margin-bottom: 12px;"
          />

        <PanelTable
          :data="filteredUsers"
          :columns="userColumns"
          @row-click="openUser"
          v-if="currentSection === 'Пользователи'"
        />
        <PanelTable
          :data="filteredСategories"
          :columns="categoriesColumns"
          v-if="currentSection === 'Категории'"
        />
        <PanelTable
          :data="filteredFormat"
          :columns="formatColumns"
          v-if="currentSection === 'Типы форматов'"
        />
        <PanelTable
          :data="filteredAge"
          :columns="ageColumns"
          v-if="currentSection === 'Возрастные категории'"
        />
        <PanelTable
          :data="filteredExcursion"
          :columns="excursionColumns"
          @row-click="openEvent"
          v-if="currentSection === 'События'"
        />
        <PanelTable
          v-if="currentSection === 'Новости'"
          :data="filteredNews"
          :columns="newsColumns"
          @row-click="openNews"
        />
        <PanelTable
          v-if="currentSection === 'Брони'"
          :data="reservation.reservations"
          :columns="reservationsColumns"
          @row-click="openReservation"
        />

        <PanelTable
          v-if="currentSection === 'Команда'"
          :data="teamData"
          :columns="teamColumns"
        />

      </div>
    </div>
    <Modal
      v-model:show="showEdit"
      title="Редактировать пользователя"
      :icon="Person"
      @submit="saveUserData"
      v-if="currentSection == 'Пользователи'"
    >
      <n-form
        ref="formRef"
        :model="userForm"
        :rules="rules"
        label-placement="top"
        require-mark-placement="right-hanging"
        autocomplete="off"
      >
        <!-- ловушки, чтобы убрать автозаполнение -->
        <input
          class="autofill-trap"
          type="text"
          name="username"
          autocomplete="username"
        />
        <input
          class="autofill-trap"
          type="password"
          name="password"
          autocomplete="current-password"
        />
        <n-grid :cols="2" :x-gap="18" :y-gap="12" path="email" responsive="screen">
          <n-form-item-gi label="Email" >
            <n-input v-model:value="userForm.email" disabled v-if="!newUser" />
            <n-input v-model:value="userForm.email" v-else />
          </n-form-item-gi>

          <n-form-item-gi label="Роль" path="role_name" required>
            <n-select v-model:value="userForm.role_name" :options="roleOptions" />
          </n-form-item-gi>

          <n-form-item-gi label="Пароль (оставьте пустым, если не меняете)" path="password">
            <n-input
              v-model:value="userForm.password"
              type="password"
              autocomplete="new-password"
              name="user_password_new"
              placeholder="Введите новый пароль"
            />
          </n-form-item-gi>

          <n-form-item-gi label="ФИО" path="full_name">
            <n-input v-model:value="userForm.full_name" />
          </n-form-item-gi>

          <n-form-item-gi label="Телефон" path="phone">
            <n-input v-model:value="userForm.phone"  />
          </n-form-item-gi>
        </n-grid>
      </n-form>
    </Modal>

    <Modal
      v-model:show="showEdit"
      title="Создать новую категорию"
      :icon="Person"
      @submit="saveCategories"
      v-if="currentSection == 'Категории'"
    >
      <label for="name">Название</label>
      <n-input name="name" v-model:value="categoriesForm.name"  placeholder="Введите название" />
    </Modal>

    <Modal
      v-model:show="showEdit"
      title="Создать новый формат"
      :icon="Person"
      @submit="saveFormat"
      v-if="currentSection == 'Типы форматов'"
    >
      <label for="name">Название</label>
      <n-input name="name" v-model:value="formatForm.name"  placeholder="Введите название" />
    </Modal>

    <Modal
      v-model:show="showEdit"
      title="Создать новую возрастную категорию"
      :icon="Person"
      @submit="saveAge"
      v-if="currentSection == 'Возрастные категории'"
    >
      <label for="name">Название</label>
      <n-input name="name" v-model:value="ageForm.name"  placeholder="Введите название" />
    </Modal>

    <Modal
      v-model:show="showEventModal"
      :title="eventMode === 'create' ? 'Создать событие' : 'Редактировать событие'"
      :icon="Person"
      @submit="submitEventFromModal"
      v-if="currentSection == 'События'"
    >
      <EventForm
        ref="eventFormRef"
        :mode="eventMode"
        :excursion="selectedExcursion"
        :excursions-stats="excursionsStats"
        :media-base-url="MEDIA_BASE_URL"
        @submit-create="createExcursion"
        @submit-edit="patchExcursion"
        @upload-photo="uploadExcursionPhoto"
        @delete-photo="deleteExcursionPhoto"
        @create-session="createExcursionSession"
        @patch-session="patchExcursionSession"
        @delete-session="deleteExcursionSession"
      />
    </Modal>

    <Modal
      v-if="currentSection === 'Новости'"
      v-model:show="showNewsModal"
      :title="newsMode === 'create' ? 'Создать новость' : 'Редактировать новость'"
      :icon="Person"
      @submit="submitNewsFromModal"
    >
      <NewsForm
        ref="newsFormRef"
        :mode="newsMode"
        :news="selectedNews"
        :photos="selectedNewsPhotos"
        :media-base-url="MEDIA_BASE_URL"
        @submit-create="createNews"
        @submit-edit="updateNews"
        @upload-photo="uploadNewsPhoto"
        @delete-photo="deleteNewsPhoto"
      />
    </Modal>

    <Modal
      v-if="currentSection === 'Брони'"
      v-model:show="showReservationModal"
      title="Детали бронирования"
      :icon="Person"
    >
      <ReservationDetails
        :reservation="selectedReservation.reservation"
        @delete="deleteFromDetails"
      />
    </Modal>

    <Modal
      v-if="currentSection === 'Команда'"
      v-model:show="showTeamModal"
      title="Сотрудник"
      :icon="Person"
      @submit="submitTeamFromModal"
    >
      <TeamForm ref="teamFormRef" @submit="createTeam" />
    </Modal>

  </n-config-provider>
</template>

<script setup>
import { useDataStore } from '@/stores/counter';
import { reactive, ref, onMounted, computed, h } from 'vue';
import { NConfigProvider, ruRU, dateRuRU } from 'naive-ui';
import BaseButton from '@/components/UI/button/BaseButton.vue';
import PanelTable from './components/panelTable.vue';
import IconButton from '@/components/UI/button/IconButton.vue';
import Modal from './components/modal.vue';
import { Person } from '@vicons/ionicons5';
import { NForm, NGrid, NFormItemGi, NInput, NSelect } from 'naive-ui'
import { notification } from '@/utils/notification';
import EventForm from './components/EventsForm.vue';
import NewsForm from './components/NewsForm.vue';
import ReservationDetails from './components/ReservationDetails.vue'
import TeamForm from './components/TeamForm.vue'

const themeOverrides = {
  common: {
    primaryColor: '#FF6C36',
    primaryColorHover: '#DD5827',
    primaryColorPressed: '#FFA280',
    primaryColorSuppl: '#FF6C36'
  }
}

const MEDIA_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://yuressa.uxp.ru' // если photo_url относительный, укажи 'https://yuressa.uxp.ru'




const showEventModal = ref(false)
const eventMode = ref('create')
const selectedExcursion = ref(null)
const eventFormRef = ref(null)

const showNewsModal = ref(false)
const newsMode = ref('create') // create | edit
const selectedNews = ref(null)
const selectedNewsPhotos = ref([])

const newsFormRef = ref(null)


const showReservationModal = ref(false)
const selectedReservation = ref(null)


async function openReservation(row) {
  const res = await store.FetchAdminReservationById(row.reservation_id)
  selectedReservation.value = res.data
  showReservationModal.value = true
}

async function deleteReservation(reservationId) {
  await store.DeleteAdminReservation(reservationId)
  await store.FetchAdminReservations()

  if (selectedReservation.value?.reservation_id === reservationId) {
    showReservationModal.value = false
    selectedReservation.value = null
  }

  notification('Бронь удалена!', 'positive')
}

async function deleteFromDetails(reservationId) {
  await deleteReservation(reservationId)
}

const reservationsColumns = [
  { title: 'ID', key: 'reservation_id', width: 70 },
  { title: 'Дата', key: 'booked_at' },
  { title: 'ФИО', key: 'full_name' },
  { title: 'Телефон', key: 'phone_number' },
  { title: 'Участники', key: 'participants_count', width: 110 },
  { title: 'Оплачено', key: 'is_paid', width: 90, render: (row) => (row.is_paid ? 'Да' : 'Нет') },
  { title: 'Статус', key: 'payment_status', width: 110 },
  { title: 'Отменено', key: 'is_cancelled', width: 110, render: (row) => (row.is_cancelled ? 'Да' : 'Нет') },
  { title: 'Экскурсия', key: 'excursion_title' },
  {
    title: 'Действие',
    key: 'actions',
    render(row) {
      return h(
        IconButton,
        {
          text: 'Удалить',
          class: 'btn-delet',
          style: { color: 'red', fontSize: '14px', padding: '5px 10px', fontWeight: '500', height: '50px' },
          onClick: async (e) => {
            e?.stopPropagation?.()
            await deleteReservation(row.reservation_id)
          }
        },
        { default: () => h('img', { src: '/icon/trash.svg', class: 'icon', alt: '' }) }
      )
    }
  }
]


const newsColumns = [
  { title: 'ID', key: 'news_id', width: 70 },
  { title: 'Заголовок', key: 'title' },
  { title: 'Создано', key: 'created_at' },
  { title: 'Автор фото', key: 'photo_author' },
  {
    title: 'Действие',
    key: 'actions',
    render(row) {
      return h(
        IconButton,
        {
          text: 'Удалить',
          class: 'btn-delet',
          style: { color: 'red', fontSize: '14px', padding: '5px 10px', fontWeight: '500', height: '50px' },
          onClick: async (e) => {
            e?.stopPropagation?.()
            await deleteNews(row.news_id)
          }
        },
        { default: () => h('img', { src: '/icon/trash.svg', class: 'icon', alt: '' }) }
      )
    }
  }
]

function openNewNews() {
  newsMode.value = 'create'
  selectedNews.value = null
  selectedNewsPhotos.value = []
  showNewsModal.value = true
}

async function openNews(row) {
  newsMode.value = 'edit'
  selectedNews.value = row
  showNewsModal.value = true

  // подгружаем photos по отдельному эндпоинту
  const res = await store.FetchAdminNewsPhotos(row.news_id)
  selectedNewsPhotos.value = res.data?.photos ?? res.data ?? []
}

async function submitNewsFromModal() {
  await newsFormRef.value?.submit()
}

async function createNews(fd) {
  await store.PostAdminNews(fd)
  await store.getAdminNews()
  showNewsModal.value = false
  notification('Новость создана!', 'positive')
}

async function updateNews({ newsId, fd }) {
  await store.PutAdminNews(newsId, fd)
  await store.FetchAdminNews()
  // обновим photos (если они отображаются)
  const res = await store.FetchAdminNewsPhotos(newsId)
  selectedNewsPhotos.value = res.data?.photos ?? res.data ?? []
  notification('Новость обновлена!', 'positive')
}

async function uploadNewsPhoto({ newsId, file }) {
  await store.PostAdminNewsPhoto(newsId, file)
  const res = await store.FetchAdminNewsPhotos(newsId)
  selectedNewsPhotos.value = res.data?.photos ?? res.data ?? []
  notification('Фото добавлено!', 'positive')
}

async function deleteNewsPhoto({ newsId, photoId }) {
  await store.DeleteAdminNewsPhoto(newsId, photoId)
  const res = await store.FetchAdminNewsPhotos(newsId)
  selectedNewsPhotos.value = res.data?.photos ?? res.data ?? []
  notification('Фото удалено!', 'positive')
}

async function deleteNews(newsId) {
  await store.DeleteAdminNews(newsId)
  await store.FetchAdminNews()
  if (selectedNews.value?.news_id === newsId) {
    showNewsModal.value = false
    selectedNews.value = null
    selectedNewsPhotos.value = []
  }
  notification('Новость удалена!', 'positive')
}


async function refreshSelected(excursionId) {
  await store.FetchAdminExcursion()
  selectedExcursion.value =
    (store.getAdminExcursion?.excursions || []).find(x => x.excursion_id === excursionId) || null
}

async function createExcursionSession({ excursionId, payload }) {
  await store.PostExcursionSession(excursionId, payload)
  await refreshSelected(excursionId)
}

async function patchExcursionSession({ excursionId, sessionId, payload }) {
  await store.PatchExcursionSession(excursionId, sessionId, payload)
  await refreshSelected(excursionId)
}

async function deleteExcursionSession({ excursionId, sessionId }) {
  await store.DeleteExcursionSession(excursionId, sessionId)
  await refreshSelected(excursionId)
}







function openNewAdmin() {
  eventMode.value = 'create'
  selectedExcursion.value = null
  showEventModal.value = true
}

function openEvent(row) {
  eventMode.value = 'edit'
  selectedExcursion.value = row
  showEventModal.value = true
}

async function submitEventFromModal() {
  await eventFormRef.value?.submit()
}

async function createExcursion(fd) {
  await store.PostNewExcursion(fd)
  await store.FetchAdminExcursion()
  showEventModal.value = false
  notification('Событие успешно создано!', 'positive')
}

async function patchExcursion({ excursionId, payload }) {
  await store.PatchExcursion(excursionId, payload)
  await store.FetchAdminExcursion()
  // подтянуть свежую версию выбранной экскурсии
  selectedExcursion.value =
    (store.getAdminExcursion?.excursions || []).find(x => x.excursion_id === excursionId) || null
  notification('Событие успешно обновлено!', 'positive')
}

async function uploadExcursionPhoto({ excursionId, file }) {
  await store.PostExcursionPhoto(excursionId, file)
  await store.FetchAdminExcursion()
  selectedExcursion.value =
    (store.getAdminExcursion?.excursions || []).find(x => x.excursion_id === excursionId) || null
  notification('Фото добавлено!', 'positive')
}

async function deleteExcursionPhoto({ excursionId, photoId }) {
  await store.DeleteExcursionPhoto(excursionId, photoId)
  await store.FetchAdminExcursion()
  selectedExcursion.value =
    (store.getAdminExcursion?.excursions || []).find(x => x.excursion_id === excursionId) || null
  notification('Фото удалено!', 'positive')
}



function fileUrl(path) {
  if (!path) return ''
  if (/^https?:\/\//i.test(path)) return path
  return MEDIA_BASE_URL.replace(/\/$/, '') + '/' + String(path).replace(/^\//, '')
}

const showTeamModal = ref(false)
const teamFormRef = ref(null)

const teamRows = computed(() => Array.isArray(store.getTeam) ? store.getTeam : [])

const teamColumns = [
  { title: 'ID', key: 'id', width: 70 },
  { title: 'ФИО', key: 'full_name' },
  { title: 'Описание', key: 'description' },
  {
    title: 'Действие',
    key: 'actions',
    render(row) {
      return h(
        IconButton,
        {
          text: 'Удалить',
          class: 'btn-delet',
          style: { color: 'red', fontSize: '14px', padding: '5px 10px', fontWeight: '500', height: '50px' },
          onClick: async (e) => {
            e?.stopPropagation?.()
            await deleteTeam(row.id)
          }
        },
        { default: () => h('img', { src: '/icon/trash.svg', class: 'icon', alt: '' }) }
      )
    }
  }
]

function openNewTeam() {
  showTeamModal.value = true
  teamFormRef.value?.reset?.()
}

async function submitTeamFromModal() {
  await teamFormRef.value?.submit()
}

async function createTeam(payload) {
  await store.PostTeam(payload)
  await store.FetchTeam()
  showTeamModal.value = false
  notification('Сотрудник добавлен!', 'positive')
}

async function deleteTeam(id) {
  await store.DeleteTeam(id)
  await store.FetchTeam()
  notification('Сотрудник удалён!', 'positive')
}




const store = useDataStore();
const currentSection = ref('Пользователи');
const users = computed(() => store.getUsers)
const categories = computed(() => store.getCategories);
const format = computed(() => store.getFormat);
const age = computed(() => store.getAge)
const excursion = computed(() => store.getAdminExcursion)
const excursionsStats = computed(() => store.getExcursionsStats)
const AdminNews = computed(() => store.getNews)
const reservation = computed(() => store.getAdminreservation)
const teamData = computed(() => store.getTeamData)

onMounted(async () => {
  try {
    await store.FetchUsers();
    await store.FetchCategories();
    await store.FetchFormat();
    await store.FetchAge();
    await store.FetchAdminExcursion();
    await store.FetchExcursionsStats();
    await store.getAdminNews();
    await store.FetchAdminReservations();
    await store.FetchTeam();
  } catch (error) {
    console.error('Ошибка при загрузке экскурсий:', error);
  }
});

// Поиск
const search = ref('')

function normalize(str) {
  return String(str ?? '').toLowerCase().trim()
}

function digitsOnly(str) {
  return String(str ?? '').replace(/\D/g, '')
}

const filteredUsers = computed(() => {
  const q = normalize(search.value)
  if (!q) return users.value

  const qDigits = digitsOnly(q)

  return users.value.filter((row) => {
    // 1) обычный поиск по тексту во всех полях
    const text = Object.values(row).map(normalize).join(' ')
    const textMatch = text.includes(q)

    // 2) доп. режим для телефона: ищем по цифрам (чтобы находило "7908..." и "+7 (908)...")
    const phoneDigits = digitsOnly(row.phone)
    const phoneMatch = qDigits && phoneDigits.includes(qDigits)

    return textMatch || phoneMatch
  })
})

const filteredСategories = computed(() => {
  const q = normalize(search.value)
  if (!q) return categories.value

  const qDigits = digitsOnly(q)

  return categories.value.filter((row) => {
    // 1) обычный поиск по тексту во всех полях
    const text = Object.values(row).map(normalize).join(' ')
    const textMatch = text.includes(q)

    // 2) доп. режим для телефона: ищем по цифрам (чтобы находило "7908..." и "+7 (908)...")
    const phoneDigits = digitsOnly(row.phone)
    const phoneMatch = qDigits && phoneDigits.includes(qDigits)

    return textMatch || phoneMatch
  })
})


const filteredFormat = computed(() => {
  const q = normalize(search.value)
  if (!q) return format.value

  const qDigits = digitsOnly(q)

  return format.value.filter((row) => {
    // 1) обычный поиск по тексту во всех полях
    const text = Object.values(row).map(normalize).join(' ')
    const textMatch = text.includes(q)

    // 2) доп. режим для телефона: ищем по цифрам (чтобы находило "7908..." и "+7 (908)...")
    const phoneDigits = digitsOnly(row.phone)
    const phoneMatch = qDigits && phoneDigits.includes(qDigits)

    return textMatch || phoneMatch
  })
})

const filteredAge = computed(() => {
  const q = normalize(search.value)
  if (!q) return age.value

  const qDigits = digitsOnly(q)

  return age.value.filter((row) => {
    // 1) обычный поиск по тексту во всех полях
    const text = Object.values(row).map(normalize).join(' ')
    const textMatch = text.includes(q)

    // 2) доп. режим для телефона: ищем по цифрам (чтобы находило "7908..." и "+7 (908)...")
    const phoneDigits = digitsOnly(row.phone)
    const phoneMatch = qDigits && phoneDigits.includes(qDigits)

    return textMatch || phoneMatch
  })
})

const filteredExcursion = computed(() => {
  const q = normalize(search.value)
  if (!q) return excursion.value.excursions

  const qDigits = digitsOnly(q)

  return excursion.value.excursions.filter((row) => {
    // 1) обычный поиск по тексту во всех полях
    const text = Object.values(row).map(normalize).join(' ')
    const textMatch = text.includes(q)

    // 2) доп. режим для телефона: ищем по цифрам (чтобы находило "7908..." и "+7 (908)...")
    const phoneDigits = digitsOnly(row.phone)
    const phoneMatch = qDigits && phoneDigits.includes(qDigits)

    return textMatch || phoneMatch
  })
})

const filteredNews = computed(() => {
  const q = normalize(search.value)
  if (!q) return AdminNews.value.news

  const qDigits = digitsOnly(q)

  return AdminNews.value.news.filter((row) => {
    // 1) обычный поиск по тексту во всех полях
    const text = Object.values(row).map(normalize).join(' ')
    const textMatch = text.includes(q)

    // 2) доп. режим для телефона: ищем по цифрам (чтобы находило "7908..." и "+7 (908)...")
    const phoneDigits = digitsOnly(row.phone)
    const phoneMatch = qDigits && phoneDigits.includes(qDigits)

    return textMatch || phoneMatch
  })
})


// Users таблица + форма
const userColumns = [
  { title: 'ID', key: 'user_id' },
  { title: 'EMAIL', key: 'email' },
  { title: 'ФИО', key: 'full_name' },
  { title: 'Телефон', key: 'phone' },
  {
    title: 'Роль',
    key: 'role',
    defaultFilterOptionValues: [],
    filterOptions: [
      { label: 'user', value: 'user' },
      { label: 'admin', value: 'admin' },
      { label: 'resident', value: 'resident' }
    ],
    filter(value, row) {
      return !!~row.role.indexOf(String(value))
    }
  },
  {
    title: 'Действие',
    key: 'actions',
    render(row) {
      return h(
        IconButton,
        {
          text: 'Удалить',
          class: 'btn-delet',
          style: { color: 'red', fontSize: '14px', padding: '5px 10px', fontWeight: '500', height: '50px' },
          onClick: (e) => {
            e?.stopPropagation?.()
            deleteUser(row.email)
          }
        },
        { default: () => h('img', { src: '/icon/trash.svg', class: 'icon', alt: '' }) }
      )
    }
  }
]

const showEdit = ref(false)
const newUser = ref(false)
const selectedUser = ref(null)

const userForm = reactive({
  email: '',
  role_name: null,
  password: '',
  full_name: '',
  phone: ''
})


function openUser(row) {
  selectedUser.value = row

  Object.assign(userForm, {
    email: row.email,
    role_name: row.role,
    full_name: row.full_name,
    phone: row.phone,
    password: ''
  })

  showEdit.value = true
}

function openNewUser() {

  Object.assign(userForm, {
    email: '',
    role_name: '',
    full_name: '',
    phone: '',
    password: ''
  })

  showEdit.value = true
  newUser.value = true
}


const roleOptions = [
  { label: 'Пользователь', value: 'user' },
  { label: 'Админ', value: 'admin' },
  { label: 'Резидент', value: 'resident' }
]

// Валидация пользовательской формы

const formRef = ref(null)

const rules = {
  role_name: [
    { required: true, message: 'Выберите роль', trigger: ['blur', 'change'] }
  ],
  full_name: [
    { required: true, message: 'Введите ФИО', trigger: ['input', 'blur'] },
    { min: 5, message: 'ФИО слишком короткое', trigger: ['input', 'blur'] }
  ],
  phone: [
    { required: true, message: 'Введите телефон', trigger: ['input', 'blur'] },
    {
      validator: (_, value) => {
        const digits = String(value || '').replace(/\D/g, '')
        return digits.length >= 10 ? true : new Error('Телефон должен содержать минимум 10 цифр')
      },
      trigger: ['input', 'blur']
    }
  ],
  password: [
    {
      validator: (_, value) => {
        if (!value) return true // пустой = не меняем пароль
        return String(value).length >= 5 ? true : new Error('Пароль минимум 5 символов')
      },
      trigger: ['input', 'blur']
    }
  ]
}

async function saveUserData() {
  try {
    await formRef.value?.validate()
    const jsonData = JSON.stringify(userForm)

    if (newUser.value) {
      await store.PostAdminNewUser(jsonData)
      newUser.value = false
      showEdit.value = false
      store.FetchUsers()
      await notification('Пользователь успешно создан!', 'positive');
    } else {
      await store.PutAdminUser(jsonData, userForm.email)
      store.FetchUsers()
      await notification('Пользователь успешно изменён!', 'positive');
    }
  } catch (e) {
    // если форма невалидна — Naive UI подсветит поля
  }
}

async function deleteUser(email) {
  try {
    await store.DeleteAdminUser(email);
    store.FetchUsers()
    notification('Пользователь успешно удалён!', 'positive')
  } catch {
    notification('Ошибка при удалении пользователя!', 'negative')
  }
}

// Таблица категорий
const categoriesColumns = [
  { title: 'ID', key: 'category_id' },
  { title: 'Название', key: 'category_name' },
  {
    title: 'Действие',
    key: 'actions',
    render(row) {
      return h(
        IconButton,
        {
          text: 'Удалить',
          class: 'btn-delet',
          style: { color: 'red', fontSize: '14px', padding: '5px 10px', fontWeight: '500', height: '50px' },
          onClick: (e) => {
            e?.stopPropagation?.()
            deleteCatigories(row.category_id)
          }
        },
        { default: () => h('img', { src: '/icon/trash.svg', class: 'icon', alt: '' }) }
      )
    }
  }
]

const categoriesForm = reactive({
  name: ''
})


function openNewCategories() {

  Object.assign(categoriesForm, {
    name: ''
  })

  showEdit.value = true
}

async function deleteCatigories (id) {
  try {
    await store.deleteCatigories(id);
    store.FetchCategories()
    notification('Категория успешно удалёна!', 'positive')
  } catch {
    notification('Ошибка при удалении категории!', 'negative')
  }
}

async function saveCategories() {
  try {
    await formRef.value?.validate()
    const jsonData = JSON.stringify(categoriesForm)
    await store.PostAdminNewCategories(jsonData)
    showEdit.value = false
    store.FetchCategories()
    await notification('Пользователь успешно создан!', 'positive');
  } catch (e) {
    // если форма невалидна — Naive UI подсветит поля
  }
}


// Таблица форм

const formatColumns = [
  { title: 'ID', key: 'format_type_id' },
  { title: 'Название', key: 'format_type_name' },
  {
    title: 'Действие',
    key: 'actions',
    render(row) {
      return h(
        IconButton,
        {
          text: 'Удалить',
          class: 'btn-delet',
          style: { color: 'red', fontSize: '14px', padding: '5px 10px', fontWeight: '500', height: '50px' },
          onClick: (e) => {
            e?.stopPropagation?.()
            deleteFormat(row.format_type_id)
          }
        },
        { default: () => h('img', { src: '/icon/trash.svg', class: 'icon', alt: '' }) }
      )
    }
  }
]

const formatForm = reactive({
  name: ''
})

async function saveFormat() {
  try {
    await formRef.value?.validate()
    const jsonData = JSON.stringify(formatForm)
    await store.PostAdminNewFormat(jsonData)
    showEdit.value = false
    store.FetchFormat()
    await notification('Пользователь успешно создан!', 'positive');
  } catch (e) {
    // если форма невалидна — Naive UI подсветит поля
  }
}

async function deleteFormat (id) {
  try {
    await store.deleteFormat(id);
    store.FetchFormat()
    notification('Формат успешно удалён!', 'positive')
  } catch {
    notification('Ошибка при удалении формата!', 'negative')
  }
}

// Таблица возраста

const ageColumns = [
  { title: 'ID', key: 'age_category_id' },
  { title: 'Название', key: 'age_category_name' },
  {
    title: 'Действие',
    key: 'actions',
    render(row) {
      return h(
        IconButton,
        {
          text: 'Удалить',
          class: 'btn-delet',
          style: { color: 'red', fontSize: '14px', padding: '5px 10px', fontWeight: '500', height: '50px' },
          onClick: (e) => {
            e?.stopPropagation?.()
            deleteAge(row.age_category_id)
          }
        },
        { default: () => h('img', { src: '/icon/trash.svg', class: 'icon', alt: '' }) }
      )
    }
  }
]

const ageForm = reactive({
  name: ''
})

async function saveAge() {
  try {
    await formRef.value?.validate()
    const jsonData = JSON.stringify(ageForm)
    await store.PostAdminNewAge(jsonData)
    showEdit.value = false
    store.FetchAge()
    await notification('Пользователь успешно создан!', 'positive');
  } catch (e) {
    // если форма невалидна — Naive UI подсветит поля
  }
}

async function deleteAge (id) {
  try {
    alert(id)
    await store.deleteAge(id);
    store.FetchAge()
    notification('Возрастная категория успешно удалена!', 'positive')
  } catch (e) {
    console.error(e)
    notification('Ошибка при удалении возрастной категории!', 'negative')
  }
}

// Таблица события

const excursionColumns = [
  { title: 'ID', key: 'excursion_id' },
  { title: 'Название', key: 'title' },
  { title: 'Краткое описание', key: 'short_description' },
  { title: 'Описание', key: 'description' },
  { title: 'Формат', key: 'category.category_name' },
  { title: 'Категория', key: 'format_type.format_type_name' },
  { title: 'Возраст', key: 'age_category.age_category_name' },
  {
    title: 'Действие',
    key: 'actions',
    render(row) {
      return h(
        IconButton,
        {
          text: 'Удалить',
          class: 'btn-delet',
          style: { color: 'red', fontSize: '14px', padding: '5px 10px', fontWeight: '500', height: '50px' },
          onClick: (e) => {
            e?.stopPropagation?.()
            deleteExcursion(row.excursion_id)
          }
        },
        { default: () => h('img', { src: '/icon/trash.svg', class: 'icon', alt: '' }) }
      )
    }
  }
]


async function deleteExcursion (id) {
  try {
    alert(id)
    await store.deleteAdminExcursion(id);
    store.FetchAdminExcursion()
    notification('Событие успешно удалено!', 'positive')
  } catch (e) {
    console.error(e)
    notification('Ошибка при удалении событии!', 'negative')
  }
}

</script>

<style scoped>
.container {
  width: 100%;
}

.loading-status {
  position: absolute;
  bottom: 0;
  right: 0;
  width: calc(100% - 323px);
  height: calc(100% - 117px);
}

.header {
  position: fixed;
  width: 100%;
  z-index: 1;
}

.main{
  /* height: calc(100vh - 166px); */
  max-height: calc(100vh - 166px);
  padding: 141px 25px 25px 348px;
}

.left-sidebar {
  position: fixed;
  top: 116px;
  height: calc(100vh - 50px);
  width: 322px;
  border-right: 1px solid #e2e8f0;
  padding: 25px 0px;
}

.title-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.title{
  width: max-content;
}

.section-header{
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-left: 25px;
  height: calc(100% + 50px);
  width: 100%;
  border-left: 1px solid #e2e8f0;
}

.nav-section {
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 0 16px;
  padding-top: 16px;
}

.nav-button {
  width: 100%;
  background: none;
  color: #333333;
  font-weight: 500;
  font-size: 20px;
}

.nav-button:hover {
  background-color: #FF895D;
}

.nav-button.active {
  background-color: #FF6C36;
  color: white;
}

.main-header {
  position: fixed;
  top: 0;
  width: 100%;
  display: flex;
  align-items: center;
  height: 66px;
  padding: 25px;
  border-bottom: 1px solid #e2e8f0;
  gap: 25px;
}

.add--btn {
  cursor: pointer;
  max-height: 50px;
}

main{
  height: 100%;
}

.main-container{
  width: 100%;
  height: 100%;
  background-color: #333333;
}

.autofill-trap {
  position: absolute;
  left: -9999px;
  top: -9999px;
  height: 0;
  width: 0;
  opacity: 0;
}
</style>
