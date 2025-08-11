<template>
  <div class="page-wrapper">
    <div class="payment-wrapper" v-if="load">
      <div class="header-wrapper">
        <h4>Редактор события</h4>
        <IconButton @click="closePage" class="close_btn"><img src="/icon/maki_cross.svg" alt=""></IconButton>
      </div>
      <div class="person-info">
        <form @submit.prevent="submitEvent">
          <h5>О событии</h5>
            <input
              type="EventName"
              name="EventName"
              placeholder="Название события*"
              v-model="formDataExcursion.title"
            >
            <textarea
              type="EventName"
              name="EventName"
              placeholder="Описание события*"
              v-model="formDataExcursion.description"
            ></textarea>
            <input
              type="EventName"
              name="EventName"
              placeholder="Формат события*"
              v-model="formDataExcursion.format_type"
            >
            <input
              type="EventName"
              name="EventName"
              placeholder="Тип события*"
              v-model="formDataExcursion.category"
            >
            <input
              type="EventName"
              name="EventName"
              placeholder="Возрастная категория*"
              v-model="formDataExcursion.age_category"
            >

            <h5>Условие проведения</h5>
            <input
              type="EventName"
              name="EventName"
              placeholder="Место сбора*"
              v-model="formDataExcursion.place"
            >
            <div class="participants-input">
              <span>Продолжительность события (в минутах)</span>
              <div class="participants">
                <IconButton class="participants--btn left--btn" type="button" @click="minusDuration" text="-"/>
                <input v-model="formDataExcursion.duration" @input="validateParticipants"/>
                <IconButton class="participants--btn right--btn" type="button" @click="plusDuration" text="+"/>
              </div>
            </div>

            <h5>Сессии события</h5>
            <div
              class="session"
              v-for="(session, i) in excursion.sessions"
              :key="i"
            >
              <p>Сессия {{ i+1 }}</p>
              <span>Дата и время события</span>
              <div class="session-date">
                <n-config-provider :locale="ruRU" :date-locale="dateRuRU">
                  <n-date-picker
                    :formatted-value="getFormattedDate(i)"
                    @update:formatted-value="setFormattedDate(i, $event)"
                    value-format="yyyy-MM-dd HH:mm"
                    type="datetime"
                    clearable
                    :time-picker-props="{
                      format: 'HH:mm',
                      hoursLabel: 'Часы',
                      minutesLabel: 'Минуты',
                      showSecond: false,
                    }"
                  />
                </n-config-provider>
                <IconButton type="button" @click="deleteSession(excursion.excursion_id, session.session_id)" class="delet-session">
                  <img src="/icon/basket red.svg" alt="">
                </IconButton>
              </div>
              <div class="participants-input">
                <span>Количество участников</span>
                <div class="participants">
                  <IconButton class="participants--btn left--btn" type="button" @click="minusParticipants(i)" text="-"/>
                  <input v-model="formDataSessions.sessions[i].max_participants" @input="validateParticipants"/>
                  <IconButton class="participants--btn right--btn" type="button" @click="plusParticipants(i)" text="+"/>
                </div>
              </div>
              <div class="participants-input">
                <span>Стоимость</span>
                <div class="participants">
                  <IconButton class="participants--btn left--btn" type="button" @click="minusPrice(i)" text="-"/>
                  <input v-model="formDataSessions.sessions[i].cost" @input="validateParticipants"/>
                  <IconButton class="participants--btn right--btn" type="button" @click="plusPrice(i)" text="+"/>
                </div>
              </div>
            </div>

            <BaseButton v-if="!addInProcess" @click="addSession()" type="button" class="sumbit--btn add-session__btn" text="Добавить сессию"/>

            <div class="new-session-action__btn">
              <BaseButton v-if="addInProcess" @click="pushSessionToApi(excursion.excursion_id)" type="button" class="add-session__btn" text="Сохранить сессию"/>
              <BaseButton v-if="addInProcess" @click="deleteNewSession()" type="button" class="delete-session__btn" text="Отмена"/>
            </div>

            <h5>Остальная информация</h5>
            <input
              type="EventName"
              name="EventName"
              placeholder="Органиатор*"
              v-model="formDataExcursion.conducted_by"
            >
            <span>Время работы организации</span>
            <input
              type="EventName"
              name="EventName"
              placeholder="Ежедневно с 10:00 до 21:00"
              v-model="formDataExcursion.working_hours"
            >
            <span>Почта для связи</span>
            <input
              type="EventName"
              name="EventName"
              placeholder="construct@ekbtour.ru"
              v-model="formDataExcursion.contact_email"
            >
            <input
              type="EventName"
              name="EventName"
              placeholder="iframe карты с местоположением"
              v-model="formDataExcursion.iframe_url"
            >
            <input
              type="EventName"
              name="EventName"
              placeholder="Telegram"
              v-model="formDataExcursion.telegram"
            >
            <input
              type="EventName"
              name="EventName"
              placeholder="Vk"
              v-model="formDataExcursion.vk"
            >
            <input
              type="EventName"
              name="EventName"
              placeholder="Дистанция от центра города (в метрах)"
              v-model="formDataExcursion.distance_to_center"
            >
            <input
              type="EventName"
              name="EventName"
              placeholder="Время от ближайшей остановки (в минутах)"
              v-model="formDataExcursion.time_to_nearest_stop"
            >
            <h5>Изображения</h5>

            <span>Текущие фото</span>
            <div class="carousel-wrapper">
              <IconButton @click="moveRight()" type="button" class="carousel_btn left-carousel_btn" v-if="excursion.photos.length > 3">
                <img src="/icon/arrow.svg" alt="">
              </IconButton>

              <div class="carousel">
                <div class="current-img-container" :style="offsetStyle">
                  <div
                    class="current-img"
                    v-for="(photo,i) in excursion.photos"
                    :key="i"
                  >
                    <img :src="baseUrl + photo.photo_url" :alt="'Фото ' + i">
                    <div class="delet-block" @click="deletePhoto(excursion.excursion_id, photo.photo_id)">
                      <svg width="50" height="50" viewBox="0 0 18 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M11.28 5.80189e-08C11.6998 0.00010886 12.1088 0.132286 12.4493 0.377808C12.7898 0.62333 13.0444 0.96975 13.177 1.368L13.72 3H17C17.2652 3 17.5196 3.10536 17.7071 3.29289C17.8946 3.48043 18 3.73478 18 4C18 4.26522 17.8946 4.51957 17.7071 4.70711C17.5196 4.89464 17.2652 5 17 5L16.997 5.071L16.13 17.214C16.0759 17.9706 15.7372 18.6786 15.182 19.1956C14.6269 19.7125 13.8965 19.9999 13.138 20H4.862C4.10346 19.9999 3.37311 19.7125 2.81797 19.1956C2.26283 18.6786 1.92411 17.9706 1.87 17.214L1.003 5.07L1 5C0.734784 5 0.48043 4.89464 0.292893 4.70711C0.105357 4.51957 0 4.26522 0 4C0 3.73478 0.105357 3.48043 0.292893 3.29289C0.48043 3.10536 0.734784 3 1 3H4.28L4.823 1.368C4.9557 0.969588 5.21043 0.623052 5.5511 0.377515C5.89176 0.131978 6.30107 -0.000101061 6.721 5.80189e-08H11.28ZM6 8C5.75507 8.00003 5.51866 8.08996 5.33563 8.25272C5.15259 8.41547 5.03566 8.63975 5.007 8.883L5 9V15C5.00028 15.2549 5.09788 15.5 5.27285 15.6854C5.44782 15.8707 5.68695 15.9822 5.94139 15.9972C6.19584 16.0121 6.44638 15.9293 6.64183 15.7657C6.83729 15.6021 6.9629 15.3701 6.993 15.117L7 15V9C7 8.73478 6.89464 8.48043 6.70711 8.29289C6.51957 8.10536 6.26522 8 6 8ZM12 8C11.7348 8 11.4804 8.10536 11.2929 8.29289C11.1054 8.48043 11 8.73478 11 9V15C11 15.2652 11.1054 15.5196 11.2929 15.7071C11.4804 15.8946 11.7348 16 12 16C12.2652 16 12.5196 15.8946 12.7071 15.7071C12.8946 15.5196 13 15.2652 13 15V9C13 8.73478 12.8946 8.48043 12.7071 8.29289C12.5196 8.10536 12.2652 8 12 8ZM11.28 2H6.72L6.387 3H11.613L11.28 2Z" fill="#e00000ff"/>
                      </svg>
                    </div>
                  </div>
                </div>
              </div>

              <IconButton @click="moveLeft(excursion.photos.length)" type="button" class="carousel_btn" v-if="excursion.photos.length > 3">
                <img src="/icon/arrow.svg" alt="">
              </IconButton>
            </div>
            <span>Фото для добавления</span>
            <n-upload
              :default-file-list="previewFileList"
              list-type="image-card"
              @preview="handlePreview"
              @change="handleFileChange"
            />
            <n-modal
              v-model:show="showModal"
              preset="card"
              style="width: 600px"
              title="A Cool Picture"
            >
              <img :src="previewImageUrl" style="width: 100%">
            </n-modal>
            <BaseButton type="submit" class="sumbit--btn" text="Сохранить изменения"/>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { ref, computed, onMounted } from 'vue';
import { useDataStore } from '@/stores/counter';
import { useRoute } from 'vue-router';
import IconButton from '@/components/UI/button/IconButton.vue';
import BaseButton from '@/components/UI/button/BaseButton.vue';
import { NDatePicker, NConfigProvider, NModal, NUpload } from 'naive-ui';
import { ruRU, dateRuRU } from 'naive-ui';
import { baseUrl } from '@/stores/counter';

const store = useDataStore();
const route = useRoute();
const load = ref(false)

const excursion = computed(() => store.getExcursionDetail.excursion);

const formDataExcursion = ref(null);
const formDataSessions = ref(null);

onMounted(async () => {
  document.body.style.overflowY = 'auto'
  try {
    await store.FetchExcursionDetailResident(route.params.id);
    setTimeout(() => {
      load.value = true
    }, 1000)
    console.log('Загрузил')
    formDataExcursion.value = {
      title: excursion.value.title,
      description: excursion.value.description,
      format_type: excursion.value.format_type.format_type_name,
      category: excursion.value.category.category_name,
      age_category: excursion.value.age_category.age_category_name,
      place: excursion.value.place,
      conducted_by: excursion.value.conducted_by,
      is_active: true,
      working_hours: excursion.value.working_hours,
      contact_email: excursion.value.contact_email,
      iframe_url: excursion.value.iframe_url,
      telegram: excursion.value.telegram,
      vk: excursion.value.vk,
      distance_to_center: excursion.value.distance_to_center,
      time_to_nearest_stop: excursion.value.time_to_nearest_stop,
      duration: excursion.value.duration,
    }

    formDataSessions.value = {
      sessions: excursion.value.sessions.map((s) => ({
        start_datetime: s.start_datetime,
        max_participants: s.max_participants,
        cost: parseFloat(s.cost),
      })),
    }
  } catch (error) {
    console.error('Ошибка при загрузке экскурсий:', error);
    alert('Произошла ошибка, попробуйте ещё раз')
  }
});

const router = useRouter();

const getFormattedDate = (index) => {
  const dt = formDataSessions.value.sessions[index].start_datetime;
  return dt ? dt.slice(0, -3).replace('T', ' ') : '';
};

const setFormattedDate = (index, value) => {
  formDataSessions.value.sessions[index].start_datetime = value.replace(' ', 'T') + ':00';
};

function closePage(){
  router.back();
}

const addInProcess = ref(false)
const newSession = ref('')

function addSession(){
  addInProcess.value = true
  newSession.value = {
    start_datetime: new Date().toISOString().split('.')[0],
    max_participants: 1,
    cost: 0,
  };

  formDataSessions.value.sessions.push(newSession.value);
  excursion.value.sessions.push(newSession.value);
}

function deleteNewSession(){
  addInProcess.value = false
  newSession.value = ''
  formDataSessions.value.sessions.pop();
  excursion.value.sessions.pop();
}

function minusDuration(){
  if (formDataExcursion.value.duration > 10){
    formDataExcursion.value.duration -= 10;
  }
}

function plusDuration(){
  formDataExcursion.value.duration += 10;
}

function minusPrice(i){
  if (formDataSessions.value.sessions[i].cost > 0){
    formDataSessions.value.sessions[i].cost -= 100;
    if(formDataSessions.value.sessions[i].cost < 0){
      formDataSessions.value.sessions[i].cost = 0;
    }
  }
}

function plusPrice(i){
  formDataSessions.value.sessions[i].cost += 100;
}

function minusParticipants(i){
  if (formDataSessions.value.sessions[i].max_participants > 1){
    formDataSessions.value.sessions[i].max_participants -= 1;
  }
}

function plusParticipants(i){
  formDataSessions.value.sessions[i].max_participants += 1;
}

// Карусель
const currentIndex = ref(0)
const imageWidth = 270 // ширина изображения + отступы

function moveLeft(total) {
  if (currentIndex.value < total - visibleCount.value) {
    currentIndex.value++
  }
}

function moveRight() {
  if (currentIndex.value > 0) currentIndex.value--
}

const visibleCount = ref(3) // Сколько видно одновременно

const offsetStyle = computed(() => ({
  transform: `translateX(-${currentIndex.value * imageWidth}px)`
}))


const showModal = ref(false);
const previewImageUrl = ref('');
const fileList = ref([]);
const previewFileList = ref([]);

const handlePreview = (file) => {
  previewImageUrl.value = file.url;
  showModal.value = true;
};

const handleFileChange = (data) => {
  fileList.value = data.fileList;
};

async function deletePhoto(excursion_id, photo_id){
  try{
    await store.DeletePhoto(excursion_id, photo_id);
    excursion.value.photos = excursion.value.photos.filter(photo => photo.photo_id !== photo_id)
  } catch(error) {
    console.error('Ошибка при удалении фото:', error);
    alert('Не удалось удалить фото');
  }
}

async function deleteSession(excursion_id, session_id) {
  try {
    await store.DeleteSession(excursion_id, session_id);
    const sessionIndex = excursion.value.sessions.findIndex(s => s.session_id === session_id);
    if (sessionIndex !== -1) {
      excursion.value.sessions.splice(sessionIndex, 1);
    }

    const formSessionIndex = formDataSessions.value.sessions.findIndex(s => s.session_id === session_id);
    if (formSessionIndex !== -1) {
      formDataSessions.value.sessions.splice(formSessionIndex, 1);
    }
  } catch (error) {
    console.error('Ошибка при удалении сессии:', error);
    alert('Не удалось удалить сессию');
  }
}


async function pushSessionToApi(excursion_id){
  const jsonData = JSON.stringify(newSession.value)
  try {
    await store.PostNewSession(excursion_id, jsonData);
    alert('Сессия добавлена');
    newSession.value = ''
    addInProcess.value = false
  } catch (error) {
    console.error('Ошибка при добавлении сессии:', error);
    alert('Не удалось удалить сессию');
  }
}

const submitEvent = async () => {
  try {
    // Создаем JSON-данные
    const jsonData = JSON.stringify(formDataExcursion.value)

    // Добавляем фото (если есть)
    if(fileList.value.length > 0){
      for (const file of fileList.value) {
        const formData = new FormData();
        formData.append('photo', file.file);

        try {
          await store.PostNewPhoto(excursion.value.excursion_id, formData);
          console.log('Файл успешно загружен:', file.name);
        } catch (error) {
          console.error('Ошибка загрузки файла:', file.name, error);
        }
      }
    }

    await store.PatchSessionData(excursion.value.excursion_id, jsonData);
    alert('Событие успешно обновленно')
    router.back();
  } catch (error) {
    console.error('Upload failed:', error);
    throw error;
  }
};
</script>

<style scoped>
.header-wrapper{
  display: flex;
  width: 100%;
  height: max-content;
  align-items: center;
  justify-content: flex-end;
  padding-bottom: 20px;
  border-bottom: 2px solid #7A797873;
}

.new-session-action__btn{
  display: flex;
  gap: 10px;
}

.page-wrapper {
  display: flex;
  justify-content: center;
  position: relative;
  min-height: calc(100vh - 100px);
}

.payment-wrapper{
  width: 100%;
  max-width: 1800px;
}

h4{
  flex: 1;
  text-align: center;
  margin: 0;
}

.close_btn{
  width: 23px;
  height: 23px;
  padding: 4px;
  border-radius: 5px;
  border: none;
  background-color: #EDEDED8A;
}

form {
  display: flex;
  flex-direction: column;
  width: 60%;
  margin-bottom: 30px;
  gap: 20px;
}

.person-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  max-width: 1800px;
  position: relative;
  margin-top: 30px;
}

input, textarea {
  font-family: 'Manrope', Arial, Helvetica, sans-serif;
  font-size: 20px;
  font-weight: 400;
  padding: 15px 0;
  border: 2px solid #2C2C2C24;
  border-radius: 8px;
  padding-left: 20px;
  /* transition: all 0.5s ease; */
}

input:focus, textarea:focus {
  outline: none;
  background-color: #F3F3F3;
}

.participants-input{
  display: flex;
  flex-direction: column;
  gap: 10px;
  color: #9E9E9E;
}

span{
  color: #9E9E9E;
}

.add-session__btn{
  background-color: #138f13;
}

.add-session__btn:hover{
  background-color: #308530;
}

.delete-session__btn{
  background-color: #dd0e0e;
}

.delete-session__btn:hover{
  background-color: red;
}

.participants{
  display: flex;
  max-width: 150px;
  margin-bottom: 10px;
}

.participants > input {
  width: 45px;
  padding: 0;
  border: none;
  text-align: center;
  border: 2px solid #E2E2E2;
  border-width: 2px 0;
  border-radius: 0;
}

.participants--btn{
  border: 2px solid #E2E2E2;
  padding: 10px 16px;
  border-radius: 12px 0 0 12px;
}

.left--btn{
  border-radius: 12px 0 0 12px;
}

.right--btn{
  border-radius: 0 12px 12px 0;
}

.carousel-wrapper{
  display: flex;
  width: 100%;
  align-items: center;
  gap: 25px;
}

.carousel{
  position: relative;
  display: flex;
  width: 100%;
  height: 200px;
  align-items: center;
  overflow: hidden;
}

.current-img-container{
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: left;
  gap: 20px;
  left: 0px;
  transition: all 0.5s ease;
}

.carousel_btn{
  width: 23px;
  height: 23px;
  padding: 4px;
  border-radius: 5px;
  border: none;
  background-color: #EDEDED8A;
}

.current-img{
  position: relative;
  max-width: max-content;
  max-height: max-content
}

.delet-block{
  position: absolute;
  content: '';
  display: flex;
  align-items: center;
  justify-content: center;
  width: 250px;
  height: 100%;
  background-color: rgba(226, 223, 223, 0.534);
  /* background-image: url(/icon/basket.svg);
  background-repeat: no-repeat;
  background-position: center;
  background-size: 50px; */
  top: 0px;
  z-index: 999;
  opacity: 0;
  transition: all 0.3s ease;
}

.delet-block:hover{
  opacity: 1;
}


.left-carousel_btn * img{
  transform: rotate(180deg);
}

.current-img > img{
  display: block;
  width: 250px;
}

.session{
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.session-date{
  display: flex;
  width: 100%;
  align-items: center;
  gap: 20px;
}

:deep(.n-config-provider){
  width: 100%;
}

.delet-session{
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 5px;
  padding: 10px;
}

.delet-session * img{
  width: 30px;
  height: 30px;
}
</style>
