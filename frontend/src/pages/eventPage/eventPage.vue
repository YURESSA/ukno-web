<template>
  <div class="page-wrapper" v-if="load">
    <div class="event-wrapper">
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
      <div class="content">
        <div class="info">
          <div class="all-info">
            <div class="left-side">
              <div class="info-block">
                <img src="/icon/event/fluent_person-24-regular.svg" alt="">
                <p>Проводит {{ excursion.conducted_by }}</p>
              </div>
              <div class="info-block">
                <img src="/icon/event/placemark.svg" alt="">
                <p>{{ getData }}, с {{ getTime }} до {{ totalTime }}</p>
              </div>
            </div>
            <div class="right-side">
              <div class="info-block">
                <img src="/icon/event/datamark.svg" alt="">
                <p>{{ getData }}, с {{ getTime }} до {{ totalTime }}</p>
              </div>
              <div class="info-block">
                <img src="/icon/event/money.svg" alt="">
                <p>{{ excursion.sessions[0].cost }} ₽</p>
              </div>
              <div class="info-block">
                <img src="/icon/event/time.svg" alt="">
                <p>{{ excursion.duration / 60 }} ч.</p>
              </div>
            </div>
          </div>
          <div class="date">
            <h2>{{ getData }}</h2>
          </div>
        </div>
      </div>
      <div class="important">
        <img src="/icon/event/exclamation.svg" alt="">
        <div class="important-content">
          <p class="large-text"><b>Важно:</b></p>
          <p class="large-text">- {{ EventFormat.type }}</p>
          <p class="large-text">- {{ EventFormat.remained_places }}</p>
          <p class="large-text">- Экскурсии  {{ excursion.age_category.age_category_name }}</p>
        </div>
      </div>
      <div class="descript">
        <h3>Подробнее об экскурсии</h3>
        <h5>Экскурсия «{{ excursion.title }}»</h5>
        <p>{{ excursion.description }}</p>
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
    <h3>Загрузка данных...</h3>
  </div>
</template>

<script setup>
import { onMounted, computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useDataStore } from '@/stores/counter';
import { baseUrl } from '@/stores/counter';
import IconButton from '@/components/UI/button/IconButton.vue';
import Contact from '../../components/shared/contact-block.vue';

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
  try {
    await store.FetchExcursionDetail(route.params.id);
    setTimeout(() => {
      load.value = true
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
}

.loading{
  text-align: center;
}

.page-wrapper::before {
  content: '';
  position: absolute;
  top: -120px;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('/backgroung/eventsFeed.png') no-repeat;
  background-size: 100% auto;
  z-index: -1;
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
}

:deep(.contact-container){
  box-shadow: 0px 2px 35.8px 0px #00000040;
}
</style>
