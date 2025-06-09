<template>
  <div class="card-wrapper" v-if="excursion && excursion.photos">
    <div class="preview-img">
      <img
        :src="getMainImage"
        :alt="excursion.title"
        @error="handleImageError"
        class="event-image"
      >
    </div>
    <div class="content">
      <div class="title">
        <h5>{{ excursion.title }}</h5>
      </div>

      <div class="descript">
        <p>{{ excursion.description }}</p>
        <p v-if="nearestSession">
          {{ formattedDate }} | {{ formattedTime }} | {{ excursion.category.category_name }}
        </p>
        <p v-else>
          Нет запланированных сеансов
        </p>
      </div>
      <div class="price">
        <span>{{ nearestSession ? `${nearestSession.cost} ₽` : 'Бесплатно>' }}</span>
      </div>
    </div>
    <IconButton
      class="event--btn"
      text="записаться"
      :disabled="!nearestSession"
      :id="props.excursion.id"
      @click="goToEventPage"
    >
      <img src="/icon/arrow.svg" alt="">
    </IconButton>
  </div>
  <div v-else class="loading">
    Загрузка данных...
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import IconButton from '@/components/UI/button/IconButton.vue';
import { baseUrl } from '@/stores/counter';

const props = defineProps({
  excursion: {
    type: Object,
    required: true
  }
});

const router = useRouter();

const goToEventPage = () => {
  router.push(`/events/${props.excursion.excursion_id}`);
};

console.log(props.excursion)

const nearestSession = computed(() => {
  if (!props.excursion.sessions || props.excursion.sessions.length === 0) return null;

  const now = new Date();
  const futureSessions = props.excursion.sessions.filter(session =>
    new Date(session.start_datetime) > now
  );

  return futureSessions.length > 0
    ? futureSessions[0]
    : props.excursion.sessions[0];
});

const formattedDate = computed(() => {
  if (!nearestSession.value) return '';
  const date = new Date(nearestSession.value.start_datetime);
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });
});

const formattedTime = computed(() => {
  if (!nearestSession.value) return '';
  const date = new Date(nearestSession.value.start_datetime);
  return date.toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit'
  });
});

const getMainImage = computed(() => {
  console.log( baseUrl + props.excursion.photos[0].photo_url)
  return baseUrl + props.excursion.photos[0].photo_url;
});

const handleImageError = (e) => {
  e.target.src = '/develop/2025-05-01 00.11.54 1.png';
};
</script>

<style scoped>
.card-wrapper{
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 20px;
  padding: 20px;

  border: 1px solid black;
  border-radius: 15px;

  max-width: 400px;
}

.title > h5{
  min-height: 80px;
}

.preview-img > img{
  display: block;
  width: 100%;
  height: 266px;
  object-fit: cover;
  border-radius: 15px;
}

.content{
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 20px;
  margin-top: 10px;
  height: 100%;
}

.descript{
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;

}

.price{
  width: 150px;
  text-align: center;
  background-color: #FFD6BD;
  color: #F25C03;
  border-radius: 30px;

  font-size: 16px;
  font-weight: 700;
}

.event--btn{
  width: 100%;
}
</style>
