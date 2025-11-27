<template>
  <div class="card-wrapper">
    <div class="favorite">
      <img src="/public/assets/icon/heart.svg" alt="">
    </div>
    <div class="img">
      <img :src="getMainImage" alt="">
    </div>
    <div class="title">
      <h3>{{ book.title }}</h3>
    </div>
    <div class="description">
      <p>{{ book.description }}</p>
    </div>
    <div class="rating">
      <div class="star">
        <img src="/public/assets/icon/feather.svg" alt="">
        <span>4,5</span>
      </div>
      <div class="comments">
        <img src="/public/assets/icon/comment-vector.svg" alt="">
        <span>1232</span>
      </div>
    </div>
    <NButton type="primary" style="width: 90%; height: 30px;" @click="routeToBooking">Забронировать</NButton>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { NButton } from 'naive-ui';
import { baseUrl } from '@/stores/counter';
import router from '@/router';



const props = defineProps({
  book: {
    type: Object,
    required: true
  }
});

const getMainImage = computed(() => {
  console.log( baseUrl + props.book.images[0].file_path)
  return baseUrl + props.book.images[0].file_path;
});

function routeToBooking(){
  const id = props.book.id
  router.push(`/booking/${id}`)
}
</script>

<style scoped>
.card-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 170px;
  gap: 4px;
  padding: 10px 5px;
  background-color: #F3F3F3;
  border-radius: 14px;
  position: relative;
}

.img {
  flex: 1;
  margin-top: 20px;
}

.img > img {
  width: 90px;
}

.description > p {
  font-size: 10px;
}

.description {
  max-width: 100%; /* Или конкретная ширина */
}

.description p {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  margin: 0; /* Убираем стандартные отступы */
}

span {
  font-size: 10px;
  color: #999;
}

.rating{
  display: flex;
  justify-content: flex-start;
  width: 90%;
  gap: 10px;
}

.star, .comments {
  display: flex;
  gap: 3px;
  align-items: center;
}

.favorite {
  position: absolute;
  right: 10px;
  top: 6px;
}


</style>
