<template>
  <div class="page-wrapper page--margin" v-if="load">
    <div class="asterick"></div>

    <div class="event-wrapper" v-if="!$isMobile()">
      <span><RouterLink to="/">Главная</RouterLink> / <RouterLink to="/events">События</RouterLink> / {{ excursion.title }}</span>
      <div class="title">
        <h2>{{ excursion.title }}</h2>
      </div>
      <div class="preview-img">
        <img
          :src="getMainImage"
          :alt="excursion.title"
          @error="handleImageError"
          class="event-image"
        >
      </div>

      <div class="container">
        <div class="events-list">
          <div class="four-event">
            <div class="event-type">
              <div class="title">
                <h3>Автор</h3>
              </div>
              <div class="event-content">
                <p>Проводит {{ excursion.conducted_by }}</p>
              </div>
            </div>
            <div class="event-type border-left">
              <div class="title">
                <h3>Место</h3>
              </div>
              <div class="event-content">
                <p>{{ excursion.place }}</p>
              </div>
            </div>
            <div class="event-type border-top">
              <div class="title">
                <h3>Стоимость</h3>
              </div>
              <div class="event-content">
                <p v-if="selectedCost > 0">{{ selectedCost }} ₽</p>
                <p v-else> Бесплатно! </p>
              </div>
            </div>
            <div class="event-type orange-block">
              <div class="title">
                <h3>Дата и время</h3>
              </div>
              <div class="event-content">
                <h2>{{ getData }}</h2>
                <p>с {{ getTime }} до {{ totalTime }} </p>
              </div>
            </div>
          </div>
          <div class="one-event-wrapper">
            <div class="one-event">
              <div class="title">
                <h3>Важно</h3>
              </div>
              <div class="event-content">
                <div class="important-content">
                  <p class="large-text">- {{ EventFormat.type }}</p>
                  <p class="large-text">- {{ EventFormat.remained_places }}</p>
                  <p class="large-text">- Экскурсии  {{ excursion.age_category.age_category_name }}</p>
                  <p class="large-text">- Продолжительность - {{ excursion.duration }} минут</p>
                </div>
              </div>
            </div>
            <div class="important-icon"></div>
          </div>
        </div>
      </div>
      <!-- Выбор сессии -->
      <div class="sessions-section" v-if="excursion.sessions.length > 0">
        <h3>Выберите дату и время</h3>
        <div class="sessions-list">
          <button
            v-for="session in excursion.sessions"
            :key="session.session_id"
            type="button"
            class="session-card"
            :class="{ 'session-card--active': selectedSession?.session_id === session.session_id, 'session-card--full': session.available <= 0 }"
            :disabled="session.available <= 0"
            @click="selectedSession = session"
          >
            <span class="session-date">{{ formatSessionDate(session) }}</span>
            <span class="session-time">{{ formatSessionTime(session) }}</span>
            <span class="session-seats" :class="{ 'session-seats--low': session.available <= 3 && session.available > 0 }">
              <template v-if="session.available > 0">{{ session.available }} мест{{ session.available === 1 ? 'о' : session.available < 5 ? 'а' : '' }}</template>
              <template v-else>Мест нет</template>
            </span>
            <span class="session-cost" v-if="parseInt(session.cost) > 0">{{ parseInt(session.cost) }} ₽</span>
            <span class="session-cost" v-else>Бесплатно</span>
          </button>
        </div>
      </div>

      <IconButton
        class="event--btn"
        text="Записаться"
        :disabled="!selectedSession || selectedSession.available <= 0"
        @click="moveToBooked"
      >
        <img src="/icon/arrow.svg" alt="">
      </IconButton>
      <div class="descript">
        <h3>Подробнее об экскурсии</h3>
        <h5>Экскурсия «{{ excursion.title }}»</h5>
        <div class="description-wrapper" v-html="safeExcursion" :class="{ 'descript-hidden': !descriptOpen }"></div>
        <button v-if="!descriptOpen" class="orange" @click="descriptOpen = !descriptOpen">Показать ещё</button>
        <button v-if="descriptOpen" class="orange" @click="descriptOpen = !descriptOpen">Скрыть описание</button>
      </div>
      <h2 v-if="excursion.photos.length > 1">Галерея ярких моментов</h2>
      <div class="gallery">
        <div
          v-for="(photo, i) in excursion.photos.slice(1)"
          :key="i"
          :class="'gallery-img img' + i"
          >
            <img :src="baseUrl + photo.photo_url" :alt="'Фото ' + i">
        </div>
      </div>
      <Contact class="map">
        <!-- Новые события: интерактивная карта по координатам -->
        <MapView
          v-if="hasCoords"
          :latitude="excursion.latitude"
          :longitude="excursion.longitude"
          :balloon-content="excursion.place"
          map-id="event-page-map-desktop"
          :height="462"
        />
        <!-- Старые события с iframe_url: показываем через iframe -->
        <template v-else-if="src !== ''">
          <iframe
            :src="src"
            width="629"
            height="462"
            frameborder="0"
            class="yand-map"
          ></iframe>
        </template>
        <span v-else>Местоположение не указано</span>
      </Contact>
    </div>

    <!-- Мобилка -->
    <div class="event-wrapper-mobile" v-else>
      <span class="route"><RouterLink to="/">Главная</RouterLink> / <RouterLink to="/events">События</RouterLink> / {{ excursion.title }}</span>
      <div class="title">
        <h2>{{ excursion.title }}</h2>
      </div>
      <div class="preview-img">
        <img
          :src="getMainImage"
          :alt="excursion.title"
          @error="handleImageError"
          class="event-image"
        >
      </div>
      <IconButton
        class="event--btn"
        text="Записаться"
        :disabled="!selectedSession || selectedSession.available <= 0"
        @click="moveToBooked"
      >
        <img src="/icon/arrow.svg" alt="">
      </IconButton>

      <!-- Выбор сессии (мобилка) -->
      <div class="sessions-section" v-if="excursion.sessions.length > 0">
        <h3>Выберите дату и время</h3>
        <div class="sessions-list">
          <button
            v-for="session in excursion.sessions"
            :key="session.session_id"
            type="button"
            class="session-card"
            :class="{ 'session-card--active': selectedSession?.session_id === session.session_id, 'session-card--full': session.available <= 0 }"
            :disabled="session.available <= 0"
            @click="selectedSession = session"
          >
            <span class="session-date">{{ formatSessionDate(session) }}</span>
            <span class="session-time">{{ formatSessionTime(session) }}</span>
            <span class="session-seats" :class="{ 'session-seats--low': session.available <= 3 && session.available > 0 }">
              <template v-if="session.available > 0">{{ session.available }} мест{{ session.available === 1 ? 'о' : session.available < 5 ? 'а' : '' }}</template>
              <template v-else>Мест нет</template>
            </span>
            <span class="session-cost" v-if="parseInt(session.cost) > 0">{{ parseInt(session.cost) }} ₽</span>
            <span class="session-cost" v-else>Бесплатно</span>
          </button>
        </div>
      </div>

      <div class="mobile-container">
        <div class="events-list-mobile">
          <div class="event-type-mobile">
            <div class="content-icon">
              <img src="/icon/eventPage/calendar.svg" alt="">
            </div>
            <div class="event-content">
              <h2>{{ getData }}</h2>
              <p>с {{ getTime }} до {{ totalTime }} </p>
            </div>
          </div>
          <div class="event-type-mobile">
            <div class="content-icon">
              <img src="/icon/eventPage/person.svg" alt="">
            </div>
            <div class="event-content">
              <p>Проводит {{ excursion.conducted_by }}</p>
            </div>
          </div>
          <div class="event-type-mobile">
            <div class="content-icon">
              <img src="/icon/eventPage/wallet.svg" alt="">
            </div>
            <div class="event-content">
              <p v-if="selectedCost > 0">{{ selectedCost }} ₽</p>
              <p v-else> Бесплатно! </p>
            </div>
          </div>
          <div class="event-type-mobile">
            <div class="content-icon">
              <img src="/icon/eventPage/ping.svg" alt="">
            </div>
            <div class="event-content">
              <p>{{ excursion.place }}</p>
            </div>
          </div>
          <div class="event-type-mobile">
            <div class="content-icon">
              <img src="/icon/eventPage/important.svg" alt="">
            </div>
            <div class="event-content">
              <div class="important-content">
                <p class="large-text">- {{ EventFormat.type }}</p>
                <p class="large-text">- {{ EventFormat.remained_places }}</p>
                <p class="large-text">- Экскурсии  {{ excursion.age_category.age_category_name }}</p>
                <p class="large-text">- Продолжительность - {{ excursion.duration }} минут</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="descript">
        <h3>Подробнее об экскурсии</h3>
        <h5 style="font-size: 16px;">Экскурсия «{{ excursion.title }}»</h5>
        <div class="description-wrapper" v-html="safeExcursion" :class="{ 'descript-hidden': !descriptOpen }"></div>
        <button v-if="!descriptOpen" class="orange" @click="descriptOpen = !descriptOpen">Показать ещё</button>
        <button v-if="descriptOpen" class="orange" @click="descriptOpen = !descriptOpen">Скрыть описание</button>
      </div>
      <h2 v-if="excursion.photos.length > 1">Галерея ярких моментов</h2>
      <div class="gallery">
        <div
          v-for="(photo, i) in excursion.photos.slice(1)"
          :key="i"
          :class="'gallery-img img' + i"
          >
            <img :src="baseUrl + photo.photo_url" :alt="'Фото ' + i">
        </div>
      </div>
      <Contact class="map">
        <!-- Новые события: интерактивная карта по координатам -->
        <MapView
          v-if="hasCoords"
          :latitude="excursion.latitude"
          :longitude="excursion.longitude"
          :balloon-content="excursion.place"
          map-id="event-page-map-mobile"
          :height="242"
        />
        <!-- Старые события с iframe_url: показываем через iframe -->
        <template v-else-if="src !== ''">
          <iframe
            :src="src"
            width="100%"
            height="242"
            frameborder="0"
            class="yand-map"
          ></iframe>
        </template>
        <span v-else>Местоположение не указано</span>
      </Contact>
    </div>
  </div>

  <div v-else class="loading">
    <Loading/>
     <!-- <h3>Загрузка...</h3> -->
  </div>
</template>

<script setup>
import { onMounted, computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useDataStore } from '@/stores/counter';
import { baseUrl } from '@/stores/counter';
import IconButton from '@/components/ui/button/IconButton.vue';
import Contact from '../../components/shared/contact-block.vue';
import Loading from '@/components/shared/loading-animation.vue';
import MapView from '@/components/shared/MapView.vue';
import { notification } from '@/utils/notification'
import DOMPurify from 'dompurify';

const store = useDataStore();
const route = useRoute();
const router = useRouter();
const load = ref(false);
const descriptOpen = ref(false);

const excursion = computed(() => store.getExcursionDetail);
const safeExcursion = computed(() => DOMPurify.sanitize(excursion.value.description));

const selectedSession = ref(null);

const selectedCost = computed(() => {
  const session = selectedSession.value ?? excursion.value.sessions[0];
  return parseInt(session?.cost || 0);
});

const hasCoords = computed(() =>
  excursion.value?.latitude != null && excursion.value?.longitude != null
);

const src = computed(() => {
  const iframeUrl = excursion.value?.iframe_url;
  if (!iframeUrl) return '';

  try {
    const parser = new DOMParser();
    const doc = parser.parseFromString(iframeUrl, 'text/html');
    const iframe = doc.querySelector('iframe');
    return iframe?.getAttribute('src') || '';
  } catch (error) {
    console.error('Ошибка при парсинге iframe:', error);
    return '';
  }
});

onMounted(async () => {
  document.body.style.overflow = 'hidden'
  try {
    await store.FetchExcursionDetail(route.params.id);
    setTimeout(() => {
      load.value = true
      document.body.style.overflow = 'auto'
      const first = excursion.value.sessions?.find(s => s.available > 0);
      selectedSession.value = first ?? excursion.value.sessions?.[0] ?? null;
    }, 1000)
  } catch (error) {
    console.error('Ошибка при загрузке экскурсий:', error);
    await notification('Произошла ошибка, попробуйте ещё раз', 'negative');
  }
});

const moveToBooked = () => {
  if (!selectedSession.value) return;
  router.push({
    path: `/payment/${selectedSession.value.session_id}`,
    query: { excursion_id: excursion.value.excursion_id }
  });
};

const getMainImage = computed(() => {
  return baseUrl + '/' + excursion.value.photos[0].photo_url;
});


const getData = computed(() => {
  const session = selectedSession.value ?? excursion.value.sessions[0];
  const date = new Date(session.start_datetime);
  const day = date.getDate().toString().padStart(2, '0');
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  return `${day}.${month}`;
});

const getTime = computed(() => {
  const session = selectedSession.value ?? excursion.value.sessions[0];
  const date = new Date(session.start_datetime);
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${hours}:${minutes}`;
});

const totalTime = computed(() => {
  const session = selectedSession.value ?? excursion.value.sessions[0];
  const date = new Date(session.start_datetime);
  date.setMinutes(date.getMinutes() + excursion.value.duration);
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${hours}:${minutes}`;
});

function formatSessionDate(session) {
  const d = new Date(session.start_datetime);
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' });
}

function formatSessionTime(session) {
  const d = new Date(session.start_datetime);
  return d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
}

const EventFormat = computed(() => {
  const format = excursion.value.format_type.format_type_name;
  const session = selectedSession.value ?? excursion.value.sessions[0];
  switch(format){
    case "Индивидуальная":
      return {type: 'Событие проходит в формате индивидуальной экскурсии', remained_places: `Всего мест ${session.max_participants} человек`}
    case "Групповая":
      return {type: 'Событие проходит в формате групповой экскурсии', remained_places: `Группа до ${session.max_participants} человек`}
    case "Мини-группа":
      return {type: 'Событие проходит в формате групповой экскурсии', remained_places: `Группа до ${session.max_participants} человек`}
    default:
      return {
        type: 'Формат экскурсии не указан',
        remained_places: ''
      };
  }
});
</script>


<style scoped>
.page-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  padding-top: 40px;
  overflow-x: hidden;
}

span{
  display: block;
  text-align: left;
  width: 100%;
  font-size: 16px;
  font-weight: 400;
  color: #2d3748;
  margin-bottom: 20px;
}

span > a{
  font-size: 16px;
  font-weight: 400;
  color: #525252;
}

.loading{
  overflow: hidden;
}

.event-wrapper{
  width: 100%;
  max-width: 1400px;
}

.preview-img > img {
  display: block;
  width: 100%;
  height: 285px;
  object-fit: cover;
  object-position: center;
}

.preview-img {
  width: 100%;
  overflow: hidden;
  border-radius: 20px;
  margin-top: 60px;
  margin-bottom: 47px;
}

.event--btn{
  width: 100%;
  margin-top: 30px;
  margin-bottom: 45px;
  background-color: #FF6C36;
  color: white;
  border: none;
}

.event--btn * img{
  filter: invert(1) brightness(1.5);
}

.content{
  width: 100%;
  margin-top: 70px;
  border-bottom: 1px solid #726F6C;
}

.info{
  display: flex;

}

.all-info{
  display: flex;
  justify-content: space-around;
  width: 100%;
  padding-right: 70px;
  padding-bottom: 30px;
}

.info-block{
  display: flex;
  gap: 10px;
  align-items: center;
}

.right-side, .left-side{
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.date{
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30%;
  padding-left: 50px;
  border-left: 1px solid #726F6C;
}

.important{
  width: 100%;
  display: flex;
  align-items: center;
  margin-top: 50px;
  padding-bottom: 40px;
  gap: 50px;
  border-bottom: 1px solid #726F6C;
}

.descript{
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 50px;
  margin-bottom: 40px;
  padding-bottom: 30px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.55);
}

.descript > button {
  all: unset;
  color: #F25C03;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
}

.description-wrapper {
  position: relative;
  max-height: 1000px;
  transition: max-height 0.3s ease-out;
  overflow: hidden;
}

.description-wrapper::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100px;
  background: linear-gradient(180deg, transparent 0%, #fff 100%);
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s linear;
}

.descript-hidden {
  max-height: 100px;
}

.descript-hidden::after {
  opacity: 1;
}

.gallery{
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
  margin-top: 20px;
  margin-bottom: 35px;
}

.gallery-img {
  height: 310px;
  overflow: hidden;
  position: relative;
  border-radius: 8px;
}

.img0, .img3 {
  width: 38%;
}

.img1, .img2 {
  width: 59%;
}

.gallery-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}


.event-type * h3, .one-event * h3{
  font-weight: 500;
}

.container{
  max-width: 1800px;
  border: 2px solid #F25C03;
  border-radius: 14px;
  margin-bottom: 30px;
}

.events-list{
  display: flex;
}

.four-event{
  display: flex;
  flex-wrap: wrap;
  width: 66%;
}

.event-type{
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: calc(50% - 51px);
  height: 310px;
  padding: 30px 20px 30px 30px;
}

.one-event{
  display: flex;
  height: calc(100% - 55px);
  flex-direction: column;
  justify-content: space-between;
  padding: 30px 60px 25px 40px;
  border-left: 2px solid #f25c03;
  border-radius: 14px;
  background-color: white;
  position: relative;
}

.one-event > .event-content{
  position: absolute;
  bottom: 25px;
  z-index: 9;
}

.one-event > .title{
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.border-left{
  border-left: 2px solid #F25C03;
  border-radius: 14 0 0 0px;
}

.border-top{
  border-top: 2px solid #F25C03;
  border-radius: 14px 0 0 0;
}

.orange-block{
  background-color: #FF6C36;
  color: #FFFFFF!important;
  border: 2px solid #F25C03;
  border-right: none;
  border-bottom: none;
  background-image: url(/icon/event/flower.svg);
  background-repeat: no-repeat;
  background-position: right;
  background-size: 90%;
}

.orange-block * h2{
  color: #FFFFFF!important;
}

.one-event-wrapper{
  position: relative;
  width: 35%;
  border-radius: 10px 10px 10px 0;
  background-color: #FF6C36;
  overflow: hidden;
}

.important-icon{
  content: '';
  position: absolute;
  width: 156px;
  height: 100%;
  background-image: url('/icon/event/important.svg');
  background-repeat: no-repeat;
  background-size: cover;
  top: 0px;
  right: 0px;
  z-index: 1;
}

.asterick{
  display: inline;
  position: absolute;
  content: '';
  width: 355px;
  height: 343px;
  background-image: url(/icon/news/asterisk.svg);
  z-index: -1;
  top: 30px;
  right: -135px;
}

@media (max-width: 768px) {
  .asterick{
    display: none;
  }
  .route{
    display: none;
  }
  .preview-img{
    margin-top: 20px;
    margin-bottom: 0;
  }
  .preview-img > img {
    height: 115px;
  }

  .gallery {
    display: flex;
    flex-wrap: nowrap;
    flex-direction: row;
    overflow-x: auto;
    overflow-y: hidden;
    width: 100%;
    max-width: 100vw;
    margin-left: -16px;
    margin-right: -16px;
    padding: 0 16px 16px 16px;
    scrollbar-width: thin;
    -webkit-overflow-scrolling: touch;
  }

  .gallery::-webkit-scrollbar {
    height: 4px;
  }

  .gallery::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
  }

  .gallery::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 10px;
  }

  .gallery-img {
    flex: 0 0 auto;
    width: 80vw;
    max-width: 300px;
    height: 200px;
    margin-right: 20px;
  }

  .img0, .img1, .img2, .img3 {
    width: 80vw !important;
    max-width: 300px !important;
  }

  .gallery-img:last-child {
    margin-right: 0;
  }

  .gallery-img img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 12px;
  }

  .descript > button {
    font-size: 16px;
  }
}

.event-wrapper-mobile{
  width: 100%;
  max-width: 100%;
}

.event--btn{
  font-size: 16px;
  margin-top: 20px;
}

.events-list-mobile{
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.event-type-mobile {
  display: flex;
  flex-direction: row;
  gap: 20px;
}

.sessions-section {
  margin: 30px 0;
  width: 100%;
}

.sessions-section h3 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #2d3748;
}

.sessions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.session-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 15px 20px;
  border: 2px solid #FFD6BD;
  border-radius: 12px;
  background-color: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 140px;
}

.session-card:hover:not(:disabled) {
  border-color: #F25C03;
  box-shadow: 0 4px 12px rgba(242, 92, 3, 0.15);
}

.session-card--active {
  border-color: #F25C03;
  background-color: #FFF5EF;
  box-shadow: 0 4px 12px rgba(242, 92, 3, 0.2);
}

.session-card:disabled, .session-card--full {
  opacity: 0.6;
  cursor: not-allowed;
  border-color: #eee;
  background-color: #fafafa;
}

.session-date {
  font-size: 16px;
  font-weight: 700;
  color: #333;
}

.session-time {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.session-seats {
  font-size: 13px;
  color: #4CAF50;
  font-weight: 600;
}

.session-seats--low {
  color: #FF9800;
}

.session-card--full .session-seats {
  color: #F44336;
}

.session-cost {
  margin-top: 8px;
  font-size: 15px;
  font-weight: 700;
  color: #F25C03;
}
</style>
