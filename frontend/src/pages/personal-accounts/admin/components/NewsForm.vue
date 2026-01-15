<template>
  <div class="news-form">
    <form @submit.prevent="submit">
      <p class="text-standart bold">
        {{ mode === 'create' ? 'Создание новости' : `Редактировать новость #${form.news_id}` }}
      </p>

      <input type="text" placeholder="Заголовок*" v-model="form.title" required />
      <textarea placeholder="Контент*" v-model="form.content" required></textarea>
      <input type="text" placeholder="Автор фото" v-model="form.photo_author" />

      <p class="text-standart bold">Фото</p>

      <n-upload
        list-type="image-card"
        :file-list="images"
        @update:file-list="images = $event"
      />


      <div v-if="mode === 'edit'" class="photos">
        <div v-for="p in photos" :key="p.photo_id" class="photo">
          <img :src="fileUrl(p.image_path)" class="photo-img" alt="" />
          <button class="photo-remove" type="button" @click="removePhoto(p.photo_id)">×</button>
        </div>

        <div v-if="!photos.length && imagesStrings.length" class="photos">
          <div v-for="(img, idx) in imagesStrings" :key="img + idx" class="photo">
            <img :src="fileUrl(img)" class="photo-img" alt="" />
            <div class="photos-hint">Удаление доступно только через photos (id)</div>
          </div>
        </div>

        <div v-if="!photos.length && !imagesStrings.length" class="photos-empty">Фото пока нет</div>
      </div>

      <!-- CREATE/EDIT: multipart upload image[] для POST/PUT
      <div class="upload-many">
        <n-upload
          list-type="image-card"
          :file-list="images"
          @update:file-list="images = $event"
          @preview="handlePreview"
        />
        <div class="upload-many-hint">
          Для create/edit: прикреплённые файлы уйдут в поле <code>image[]</code>.
        </div>
      </div> -->

      <!-- EDIT: add single photo via /photos -->
      <div v-if="mode === 'edit'" class="upload-one">
        <n-upload
          :key="uploadKey"
          list-type="image-card"
          :max="1"
          :file-list="newPhoto"
          @update:file-list="newPhoto = $event"
          @preview="handlePreview"
        />
        <BaseButton text="Добавить фото" :disabled="!newPhoto.length" @click="uploadOnePhoto" style="font-size: 16px; padding: 5px 15px; width: 200px; height: 40px;"/>
      </div>

      <n-modal v-model:show="showPreview" preset="card" style="width: 700px" title="Предпросмотр">
        <img :src="previewUrl" style="width: 100%" />
      </n-modal>

      <button class="hidden-submit" type="submit">submit</button>
    </form>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { NModal, NUpload } from 'naive-ui'
import BaseButton from '@/components/UI/button/BaseButton.vue'

const props = defineProps({
  mode: { type: String, default: 'create' },  // create | edit
  news: { type: Object, default: null },
  photos: { type: Array, default: () => [] }, // из GET /news/{id}/photos
  mediaBaseUrl: { type: String, default: 'https://yuressa.uxp.ru' }
})

const emit = defineEmits([
  'submit-create',   // fd
  'submit-edit',     // { newsId, fd }
  'upload-photo',    // { newsId, file }
  'delete-photo'     // { newsId, photoId }
])

const form = ref(makeEmpty())
const images = ref([])   // для POST/PUT: image[]
const newPhoto = ref([]) // для /photos: photo
const uploadKey = ref(1)

const showPreview = ref(false)
const previewUrl = ref('')

function buildFormDataimg() {
  const fd = new FormData()
  fd.append('data', JSON.stringify({
    title: form.value.title,
    content: form.value.content,
    photo_author: form.value.photo_author
  }))

  // важно: берём именно f.file
  images.value.forEach(f => f?.file && fd.append('image', f.file))
  return fd
}


const imagesStrings = computed(() => Array.isArray(props.news?.images) ? props.news.images : [])

watch(
  () => props.news,
  () => {
    if (props.mode === 'edit' && props.news) {
      form.value = {
        news_id: props.news.news_id,
        title: props.news.title ?? '',
        content: props.news.content ?? '',
        photo_author: props.news.photo_author ?? ''
      }
      images.value = []
      newPhoto.value = []
      uploadKey.value++
    }
  },
  { immediate: true }
)

watch(
  () => props.mode,
  (m) => {
    if (m === 'create') {
      form.value = makeEmpty()
      images.value = []
      newPhoto.value = []
      uploadKey.value++
    }
  },
  { immediate: true }
)

function makeEmpty () {
  return { news_id: null, title: '', content: '', photo_author: '' }
}

function fileUrl(path) {
  if (!path) return ''
  if (/^https?:\/\//i.test(path)) return path
  console.log(props.mediaBaseUrl.replace(/\/$/, '') + '/' + String(path).replace(/^\//, ''))
  return props.mediaBaseUrl.replace(/\/$/, '') + '/' + String(path).replace(/^\//, '')
}

function handlePreview(file) {
  previewUrl.value = file.url
  showPreview.value = true
}

function buildFormData() {
  const dto = {
    title: form.value.title,
    content: form.value.content,
    photo_author: form.value.photo_author
  }

  const fd = new FormData()
  fd.append('data', JSON.stringify(dto))
  images.value.forEach(f => f?.file && fd.append('image', f.file)) // swagger: image array[file]
  return fd
}

function submit() {
  const fd = buildFormData()

  if (props.mode === 'create') {
    emit('submit-create', fd)
    return
  }

  emit('submit-edit', { newsId: form.value.news_id, fd })
}

function uploadOnePhoto() {
  const f = newPhoto.value?.[0]
  if (!f?.file) return
  emit('upload-photo', { newsId: form.value.news_id, file: f.file })
  newPhoto.value = []
  uploadKey.value++
}

function removePhoto(photoId) {
  emit('delete-photo', { newsId: form.value.news_id, photoId })
}

defineExpose({ submit })
</script>

<style scoped>
.news-form form { display: flex; flex-direction: column; gap: 14px; width: 600px; }
input, textarea { padding: 15px 0 15px 20px; border: 2px solid #2C2C2C24; border-radius: 8px; font-size: 14px; font-family: 'Manrope'; }
textarea { min-height: 120px; resize: vertical; }
.hidden-submit { display: none; }

.photos { display: flex; gap: 12px; flex-wrap: wrap; }
.photo { position: relative; width: 160px; height: 110px; overflow: hidden; border-radius: 10px; border: 1px solid #eee; background: #fafafa; }
.photo-img { width: 100%; height: 100%; object-fit: cover; }
.photo-remove { position: absolute; right: 6px; top: 6px; width: 26px; height: 26px; border-radius: 8px; border: none; background: rgba(0,0,0,0.55); color: #fff; cursor: pointer; }
.photos-empty { color: #9E9E9E; }
.photos-hint { position: absolute; left: 6px; bottom: 6px; right: 6px; font-size: 10px; color: #fff; background: rgba(0,0,0,0.55); padding: 4px 6px; border-radius: 8px; }

.upload-one { display: flex; align-items: center; gap: 12px; }
.upload-one-btn { height: 40px; padding: 0 14px; border-radius: 10px; border: 1px solid #e2e8f0; background: #fff; cursor: pointer; }
.upload-many-hint { font-size: 12px; color: #666; margin-top: 6px; }
</style>
