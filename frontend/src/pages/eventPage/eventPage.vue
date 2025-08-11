<template>
  <div class="page-wrapper page--margin" v-if="load">
    <div class="asterick"></div>

    <div class="event-wrapper">
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
      <IconButton
        class="event--btn"
        text="записаться"
        :id="excursion.id"
        @click="moveToBooked"
      >
        <img src="/icon/arrow.svg" alt="">
      </IconButton>

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
                <p>{{ excursion.sessions[0].cost }} ₽</p>
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
      <div class="descript">
        <h3>Подробнее об экскурсии</h3>
        <h5>Экскурсия «{{ excursion.title }}»</h5>
        <p>{{ excursion.description }}</p>
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
        <iframe
        v-if="src != ''"
        :src="src"
        width="629"
        height="462"
        frameborder="0"
        class="yand-map"
        ></iframe>
        <span v-else>Произошла ошибка при загрузке карты</span>
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
import IconButton from '@/components/UI/button/IconButton.vue';
import Contact from '../../components/shared/contact-block.vue';
import Loading from '@/components/shared/loading-animation.vue';

const store = useDataStore();
const route = useRoute();
const router = useRouter();

const excursion = computed(() => store.getExcursionDetail);
const src = computed(() => {
  const iframeUrl = excursion.value?.iframe_url;
  return iframeUrl?.match(/src='(.*?)'/)?.[1] || '';
});
const load = ref(false)

onMounted(async () => {
  document.body.style.overflow = 'hidden'
  try {
    await store.FetchExcursionDetail(route.params.id);
    setTimeout(() => {
      load.value = true
      document.body.style.overflow = 'auto'
    }, 1000)
  } catch (error) {
    console.error('Ошибка при загрузке экскурсий:', error);
    alert('Произошла ошибка, попробуйте ещё раз')
  }
});

const moveToBooked = () => {
  router.push({
    path: `/payment/${excursion.value.sessions[0].session_id}`,
    query: { excursion_id: excursion.value.excursion_id }
  });
};

const getMainImage = computed(() => {
  console.log( baseUrl + excursion.value.photos[0].photo_url)
  return baseUrl + excursion.value.photos[0].photo_url;
});


const getData = computed(() => {
  const date = new Date(excursion.value.sessions[0].start_datetime);
  const day = date.getDate().toString().padStart(2, '0');
  const month = (date.getMonth() + 1).toString().padStart(2, '0');

  return `${day}.${month}`;
});

const getTime = computed(() => {
  const date = new Date(excursion.value.sessions[0].start_datetime);
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${hours}:${minutes}`;
});

const totalTime = computed(() => {
  const date = new Date(excursion.value.sessions[0].start_datetime);
  date.setMinutes(date.getMinutes() + excursion.value.duration);
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');

  return `${hours}:${minutes}`;
});

const EventFormat = computed(() => {
  const format = excursion.value.format_type.format_type_name;
  switch(format){
    case "Индивидуальная":
      return {type: 'Событие проходит в формате индивидуальной экскурсии', remained_places: `Всего мест ${excursion.value.sessions[0].max_participants} человек`}
    case "Групповая":
      return {type: 'Событие проходит в формате групповой экскурсии', remained_places: `Группа до ${excursion.value.sessions[0].max_participants} человек`}
    case "Мини-группа":
      return {type: 'Событие проходит в формате групповой экскурсии', remained_places: `Группа до ${excursion.value.sessions[0].max_participants} человек`}
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
  gap: 30px;
  margin-top: 50px;
  margin-bottom: 50px;
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
  overflow: hidden; /* Обрезаем всё, что выходит за границы */
  position: relative; /* Для корректного позиционирования img */
  border-radius: 8px; /* Опционально: скругление углов */
}

/* Размеры блоков */
.img0, .img3 {
  width: 38%;
}

.img1, .img2 {
  width: 59%;
}

/* Стили для самих изображений */
.gallery-img img {
  width: 100%; /* Занимает всю ширину родителя */
  height: 100%; /* Занимает всю высоту родителя */
  object-fit: cover; /* Сохраняет пропорции, заполняя весь блок */
  object-position: center; /* Центрирует изображение */
}

:deep(.contact-container){
  box-shadow: 0px 2px 35.8px 0px #00000040;
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

</style>
