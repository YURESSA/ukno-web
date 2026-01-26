<template>
  <div class="event-form">
    <form @submit.prevent="submit">
      <p class="text-standart bold">
        {{ mode === 'create' ? 'Создание события' : `Редактирование события #${form.excursion_id}` }}
      </p>

      <input type="text" placeholder="Название события*" v-model="form.title" required />

      <textarea placeholder="Краткое описание" v-model="form.short_description"></textarea>

      <textarea placeholder="Описание события*" v-model="form.description" required></textarea>

      <!-- API у тебя ждёт названия -->
      <select v-model="form.format_type" class="custom-select" required>
        <option class="placeholder" value="" disabled>Формат события*</option>
        <option
          class="option"
          v-for="f in (excursionsStats?.format_types || [])"
          :key="f.format_type_id"
          :value="f.format_type_name"
        >
          {{ f.format_type_name }}
        </option>
      </select>

      <select v-model="form.category" class="custom-select" required>
        <option class="placeholder" value="" disabled>Тип события*</option>
        <option
          class="option"
          v-for="c in (excursionsStats?.categories || [])"
          :key="c.category_id"
          :value="c.category_name"
        >
          {{ c.category_name }}
        </option>
      </select>

      <select v-model="form.age_category" class="custom-select" required>
        <option class="placeholder" value="" disabled>Возрастная категория*</option>
        <option
          class="option"
          v-for="a in (excursionsStats?.age_categories || [])"
          :key="a.age_category_id"
          :value="a.age_category_name"
        >
          {{ a.age_category_name }}
        </option>
      </select>

      <p class="text-standart bold">Условие проведения</p>

      <input type="text" placeholder="Место сбора*" v-model="form.place" required />

      <div class="participants-input">
        <span>Продолжительность (мин)</span>
        <div class="participants">
          <button class="participants--btn left--btn" type="button" @click="minusDuration">-</button>
          <input v-model="form.duration" @input="clampNumbers" />
          <button class="participants--btn right--btn" type="button" @click="plusDuration">+</button>
        </div>
      </div>

      <p class="text-standart bold">Остальная информация</p>

      <input type="text" placeholder="Организатор*" v-model="form.conducted_by" required />
      <input type="text" placeholder="Часы работы" v-model="form.working_hours" />
      <input type="email" placeholder="Почта для связи" v-model="form.contact_email" />
      <input type="text" placeholder="iframe карты" v-model="form.iframe_url" />
      <input type="text" placeholder="Telegram" v-model="form.telegram" />
      <input type="text" placeholder="VK" v-model="form.vk" />
      <input type="text" placeholder="До центра (км)" v-model="form.distance_to_center" />
      <input type="text" placeholder="До остановки (мин)" v-model="form.time_to_nearest_stop" />

      <!-- ФОТО -->
      <p class="text-standart bold">Фотографии</p>

      <!-- существующие фото (edit) -->
      <div v-if="mode === 'edit'" class="photos">
        <div v-for="p in existingPhotos" :key="p.photo_id" class="photo">
          <img :src="photoSrc(p.photo_url)" class="photo-img" alt="" />
          <button class="photo-remove" type="button" @click="removePhoto(p.photo_id)">×</button>
        </div>
        <div v-if="!existingPhotos.length" class="photos-empty">Фото пока нет</div>
      </div>

      <!-- create: много фото разом -->
      <div v-if="mode === 'create'">
        <n-upload
          list-type="image-card"
          :file-list="createPhotos"
          @update:file-list="createPhotos = $event"
          @preview="handlePreview"
        />
      </div>

      <!-- edit: добавление по одному фото (endpoint ждёт field 'photo') -->
      <div v-else class="upload-one">
        <n-upload
          :key="uploadKey"
          list-type="image-card"
          :max="1"
          :file-list="editPhoto"
          @update:file-list="editPhoto = $event"
          @preview="handlePreview"
        />
        <button
          type="button"
          class="upload-one-btn"
          :disabled="!editPhoto.length || uploadingPhoto"
          @click="uploadOnePhoto"
        >
          Добавить фото
        </button>
      </div>

      <n-modal v-model:show="showPreview" preset="card" style="width: 600px" title="Предпросмотр">
        <img :src="previewImageUrl" style="width: 100%" />
      </n-modal>

      <!-- СЕССИИ -->
      <p class="text-standart bold">Сессии</p>

      <!-- existing sessions in edit -->
      <div v-if="mode === 'edit'" class="sessions">
        <div v-for="s in sessionEdits" :key="s.session_id" class="session-row">
          <n-date-picker
            v-model:formatted-value="s.start_datetime"
            value-format="yyyy-MM-dd'T'HH:mm:ss"
            type="datetime"
            clearable
          />
          <label for="">Количество мест</label>
          <input class="session-input" v-model="s.max_participants" @input="clampSession(s)" placeholder="max" />
          <label for="">Цена</label>
          <input class="session-input" v-model="s.cost" @input="clampSession(s)" placeholder="cost" />
          <!-- <button type="button" class="session-btn" @click="saveSession(s)">Сохранить</button> -->
          <BaseButton text="Сохранить" style="height: 40px; padding: 5px 15px; font-size: 16px;" @click="saveSession(s)"/>
          <IconButton type="button" class="btn-delet" text="Удалить" @click="deleteSession(s.session_id)"><img src="/icon/trash.svg" class="icon" alt=""></IconButton>
        </div>

        <div class="session-create">
          <p class="text-standart bold">Добавить сессию</p>
          <div class="action">
            <n-date-picker
              v-model:formatted-value="newSession.start_datetime"
              value-format="yyyy-MM-dd'T'HH:mm:ss"
              type="datetime"
              clearable
            />

            <input class="session-input" v-model="newSession.max_participants" @input="clampSession(newSession)" placeholder="max" />
            <input class="session-input" v-model="newSession.cost" @input="clampSession(newSession)" placeholder="cost" />
          </div>
          <!-- <button type="button" class="session-btn" @click="createSession">Добавить</button> -->
          <BaseButton type="button" text="Добавить" style="font-size: 16px;" @click="createSession"/>
        </div>
      </div>

      <!-- create mode: локально можно создать >1 сессии и отправить в POST -->
      <div v-else class="sessions">
        <div v-for="(s, idx) in form.sessions" :key="idx" class="session-ow" style="display: flex; gap: 20px; align-items: end;">
          <n-date-picker
            v-model:formatted-value="s.start_datetime"
            value-format="yyyy-MM-dd'T'HH:mm:ss"
            type="datetime"
            clearable
          />
          <div class="numbers" style="display: flex; flex-direction: row; width: 100%;">
            <div class="number-cont" style="display: flex; flex-direction: column;">
              <label for="">Количество мест</label>
              <input class="session-input" v-model="s.max_participants" @input="clampSession(s)" placeholder="max" />
            </div>
            <div class="number-cont" style="display: flex; flex-direction: column;">
              <label for="">Цена</label>
              <input class="session-input" v-model="s.cost" @input="clampSession(s)" placeholder="cost" />
            </div>
          </div>
          <button type="button" class="session-btn danger" @click="removeLocalSession(idx)" v-if="form.sessions.length > 1">
            Удалить
          </button>
          <IconButton type="button" class="btn-delet" text="Удалить" @click="removeLocalSession(idx)" v-if="form.sessions.length > 1"><img src="/icon/trash.svg" class="icon" alt=""></IconButton>
        </div>


        <BaseButton type="button" text="+ Добавить сессию" @click="addLocalSession"/>
      </div>

      <button type="submit" class="hidden-submit">submit</button>
    </form>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { NDatePicker, NModal, NUpload } from 'naive-ui'
import BaseButton from '@/components/UI/button/BaseButton.vue';
import IconButton from '@/components/UI/button/IconButton.vue';

const props = defineProps({
  mode: { type: String, default: 'create' },      // create | edit
  excursion: { type: Object, default: null },
  excursionsStats: { type: Object, default: () => ({}) },
  mediaBaseUrl: { type: String, default: 'https://yuressa.uxp.ru' }
})

const emit = defineEmits([
  'submit-create',
  'submit-edit',
  'upload-photo',
  'delete-photo',
  'create-session',
  'patch-session',
  'delete-session'
])

const showPreview = ref(false)
const previewImageUrl = ref('')

let createPhotos = ref([])
let editPhoto = ref([])
const uploadingPhoto = ref(false)
const uploadKey = ref(1)

const form = ref(makeEmpty())

// редактирование сессий (копия из excursion.sessions)
const sessionEdits = ref([])
const newSession = ref(makeNewSession())

const existingPhotos = computed(() =>
  Array.isArray(props.excursion?.photos) ? props.excursion.photos : []
)

watch(
  () => props.mode,
  (m) => {
    if (m === 'create') resetCreate()
    if (m === 'edit') fillFromExcursion()
  },
  { immediate: true }
)

watch(
  () => props.excursion,
  () => {
    if (props.mode === 'edit') fillFromExcursion()
  },
  { immediate: true }
)

function makeNewSession() {
  return { start_datetime: null, max_participants: 1, cost: 0 }
}

function makeEmpty() {
  return {
    excursion_id: null,
    title: '',
    short_description: '',
    description: '',
    duration: 60,

    category: '',
    format_type: '',
    age_category: '',

    place: '',
    conducted_by: '',
    is_active: true,
    working_hours: '',
    contact_email: '',
    iframe_url: '',
    telegram: '',
    vk: '',
    distance_to_center: null,
    time_to_nearest_stop: null,

    sessions: [makeNewSession()]
  }
}

function resetCreate() {
  form.value = makeEmpty()
  createPhotos.value = []
  editPhoto.value = []
  sessionEdits.value = []
  newSession.value = makeNewSession()
  uploadKey.value++
}

function fillFromExcursion() {
  const e = props.excursion
  if (!e) return

  form.value = {
    ...makeEmpty(),
    excursion_id: e.excursion_id,
    title: e.title ?? '',
    short_description: e.short_description ?? '',
    description: e.description ?? '',
    duration: e.duration ?? 0,

    category: e.category?.category_name ?? '',
    format_type: e.format_type?.format_type_name ?? '',
    age_category: e.age_category?.age_category_name ?? '',

    place: e.place ?? '',
    conducted_by: e.conducted_by ?? '',
    is_active: !!e.is_active,
    working_hours: e.working_hours ?? '',
    contact_email: e.contact_email ?? '',
    iframe_url: e.iframe_url ?? '',
    telegram: e.telegram ?? '',
    vk: e.vk ?? '',
    distance_to_center: e.distance_to_center ?? 0,
    time_to_nearest_stop: e.time_to_nearest_stop ?? 0
  }

  // sessions edit copy
  sessionEdits.value = Array.isArray(e.sessions)
    ? e.sessions.map(s => ({
        session_id: s.session_id,
        start_datetime: s.start_datetime,
        max_participants: Number(s.max_participants || 1),
        cost: Number(s.cost || 0)
      }))
    : []

  newSession.value = makeNewSession()

  createPhotos.value = []
  editPhoto.value = []
  uploadKey.value++
}

function photoSrc(url) {
  if (!url) return ''
  if (/^https?:\/\//i.test(url)) return url
  return props.mediaBaseUrl.replace(/\/$/, '') + '/' + String(url).replace(/^\//, '')
}

function handlePreview(file) {
  previewImageUrl.value = file.url
  showPreview.value = true
}

function clampNumbers() {
  form.value.duration = Math.max(0, Number(form.value.duration || 0))
  form.value.distance_to_center = Number(form.value.distance_to_center || 0)
  form.value.time_to_nearest_stop = Number(form.value.time_to_nearest_stop || 0)
}

function clampSession(s) {
  s.max_participants = Math.max(1, Number(s.max_participants || 1))
  s.cost = Math.max(0, Number(s.cost || 0))
}

function minusDuration() { if (Number(form.value.duration) > 10) form.value.duration = Number(form.value.duration) - 10 }
function plusDuration() { form.value.duration = Number(form.value.duration) + 10 }

function addLocalSession() {
  form.value.sessions.push(makeNewSession())
}
function removeLocalSession(idx) {
  form.value.sessions.splice(idx, 1)
}

async function submit() {
  if (props.mode === 'create') {
    // нормализуем строки (сервер у тебя ищет по названию)
    const dto = {
      ...form.value,
      category: String(form.value.category || '').trim(),
      format_type: String(form.value.format_type || '').trim(),
      age_category: String(form.value.age_category || '').trim()
    }

    // если пользователь не выбрал дату — пусть упадёт, иначе сервер тоже может ругаться
    dto.sessions = (dto.sessions || []).map(s => ({
      start_datetime: String(s.start_datetime || '').trim(),
      max_participants: Number(s.max_participants || 1),
      cost: Number(s.cost || 0)
    }))

    const fd = new FormData()
    createPhotos.value.forEach(f => f?.file && fd.append('photos', f.file))
    fd.append('data', JSON.stringify(dto))
    emit('submit-create', fd)
    return
  }

  // edit: PATCH экскурсии (по твоей схеме swagger) — только эти поля
  const payload = {
    title: form.value.title,
    description: form.value.description,
    duration: Number(form.value.duration || 0),
    place: form.value.place,
    conducted_by: form.value.conducted_by,
    is_active: !!form.value.is_active,
    working_hours: form.value.working_hours,
    contact_email: form.value.contact_email,
    iframe_url: form.value.iframe_url,
    telegram: form.value.telegram,
    vk: form.value.vk,
    distance_to_center: Number(form.value.distance_to_center || 0),
    time_to_nearest_stop: Number(form.value.time_to_nearest_stop || 0)
  }

  emit('submit-edit', { excursionId: form.value.excursion_id, payload })
}

function uploadOnePhoto() {
  const f = editPhoto.value?.[0]
  if (!f?.file) return
  uploadingPhoto.value = true
  emit('upload-photo', { excursionId: form.value.excursion_id, file: f.file })
  // сбрасываем, чтобы можно было выбрать следующий файл (single file-list сценарий) [web:508]
  editPhoto.value = []
  uploadKey.value++
  uploadingPhoto.value = false
}

function removePhoto(photoId) {
  emit('delete-photo', { excursionId: form.value.excursion_id, photoId })
}

function createSession() {
  if (!newSession.value.start_datetime) return
  emit('create-session', {
    excursionId: form.value.excursion_id,
    payload: {
      start_datetime: newSession.value.start_datetime,
      max_participants: Number(newSession.value.max_participants || 1),
      cost: Number(newSession.value.cost || 0)
    }
  })
  newSession.value = makeNewSession()
}

function saveSession(s) {
  emit('patch-session', {
    excursionId: form.value.excursion_id,
    sessionId: s.session_id,
    payload: {
      start_datetime: s.start_datetime,
      max_participants: Number(s.max_participants || 1),
      cost: Number(s.cost || 0)
    }
  })
}

function deleteSession(sessionId) {
  emit('delete-session', {
    excursionId: form.value.excursion_id,
    sessionId
  })
}

defineExpose({ submit })

</script>

<style scoped>
.event-form form { display: flex; flex-direction: column; gap: 14px; }

input, textarea, select {
  padding: 15px 0;
  border: 2px solid #2C2C2C24;
  border-radius: 8px;
  padding-left: 20px;
  transition: all 0.3s ease;
  font-size: 14px;
  font-family: 'Manrope';
}

textarea { min-height: 90px; resize: vertical; }

.custom-select option.placeholder { color: #999; }
.custom-select { color: #777; }
.custom-select:valid { color: #333; }

.participants-input { display: flex; flex-direction: column; gap: 8px; color: #9E9E9E; }
span { color: #9E9E9E; }

.participants { display: flex; max-width: 180px; }
.participants > input {
  width: 60px;
  padding: 0;
  border: none;
  text-align: center;
  border: 2px solid #E2E2E2;
  border-width: 2px 0;
  border-radius: 0;
}
.participants--btn { border: 2px solid #E2E2E2; padding: 10px 16px; background: white; color: #9E9E9E; }
.left--btn { border-radius: 12px 0 0 12px; }
.right--btn { border-radius: 0 12px 12px 0; }

.photos { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 6px; }
.photo { position: relative; width: 140px; height: 90px; overflow: hidden; border-radius: 10px; border: 1px solid #eee; background: #fafafa; }
.photo-img { width: 100%; height: 100%; object-fit: cover; }
.photo-remove { position: absolute; right: 6px; top: 6px; width: 26px; height: 26px; border-radius: 8px; border: none; background: rgba(0,0,0,0.55); color: #fff; cursor: pointer; }
.photos-empty { color: #9E9E9E; }

.upload-one {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border: 1px solid #777;
  border-radius: 15px;
}
.upload-one-btn { padding: 5px 15px; border-radius: 10px; border: 1px solid #e2e8f0; background: #FF6C36; cursor: pointer; color: white; font-size: 16px;}

:deep(.btn-delet){
  background: none;
  gap: 10px;
  max-height: 30px;
  color: red;
  font-size: 14px;
  padding: 5px 10px;
  font-weight: 500;
  height: 50px;
}

:deep(.icon){
  height: 15px;
  order: 1;
}

:deep(.text){
  order: 2;
}

:deep(.btn-delet:hover){
  background: #dc3545;
  color: white;
}

:deep(.btn-delet:hover > .text){
  color: white;
}

:deep(.btn-delet:hover .icon) {
  filter: brightness(0) invert(1);
}

.sessions { display: flex; flex-direction: column; gap: 10px; }
.session-row { display: grid; grid-template-columns: 1fr 120px 120px 140px 120px; gap: 10px; align-items: center; }
.session-input { height: 40px; padding: 0 12px; }
.session-btn { height: 40px; border-radius: 10px; border: 1px solid #e2e8f0; background: #fff; cursor: pointer; }
.session-btn.danger { border-color: #ffb4b4; }
.session-create {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  width: 100%;
  gap: 10px;
}

.action {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 15px;
}

.hidden-submit { display: none; }
</style>
