<template>
  <div class="card-wrapper">
    <div class="favorite">
      <img src="/public/assets/icon/heart.svg" alt="">
    </div>
    <div class="img">
      <img :src="getMainImage" alt="">
    </div>
    <div class="title">
      <h3>{{ book.books[0].title }}</h3>
    </div>
    <div class="description end-date">
      <p>{{ book.due_date }}</p>
    </div>
    <NButton class="delet-btn" type="primary" style="width: 90%; height: 30px;" @click="deletBooked">Отменить бронь</NButton>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { NButton } from 'naive-ui';
import { baseUrl } from '@/stores/counter';
import router from '@/router';
import { useDataStore } from '@/stores/counter';


const store = useDataStore();
const props = defineProps({
  book: {
    type: Object,
    required: true
  }
});

const getMainImage = computed(() => {
  if(props.book.books[0].images.lenght !== 0){
    return new URL('/public/assets/book1.png', import.meta.url).href
  } else {
    console.log( baseUrl + props.book.books[0].images[0].file_path)
    return baseUrl + props.book.books[0].file_path;
  }
});

async function deletBooked(){
  await store.deletOrder(props.book.id);
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

:deep(.delet-btn) {
  background-color: rgb(184, 0, 0);
}

:deep(.delet-btn:active) {
  background-color: rgb(220, 0, 0);
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

/* .description p {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  margin: 0;
} */

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
