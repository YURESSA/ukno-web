<template>
  <div class="news-content" :id="'news-' + news.news_id">
    <div class="title">
      <h2>{{ news.title }}</h2>
    </div>
    <div class="created-at">
      <span>{{ formattedDate }} • УКНО: Сообщество на Урале</span>
    </div>
    <div class="news-img">
      <img
        :src="getMainImage"
        :alt="news.title"
        class="event-image"
      >
      <span>{{ news.photo_author }}</span>
    </div>
    <div class="news-text" v-html="news.content">

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { baseUrl } from '@/stores/counter';

const props = defineProps({
  news: {
    type: Object,
    required: true
  }
});

const formattedDate = computed(() => {
  const date = new Date(props.news.created_at);
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });
});

const getMainImage = computed(() => {
  return baseUrl + props.news.images[0];
});
</script>

<style lang="css" scoped>
span{
  font-family: var(--font-family);
  font-weight: 400;
  font-size: 16px;
  line-height: 150%;
  text-align: center;
  color: #525252;
}

.created-at{
  margin-bottom: 45px;
}

.news-content{
  margin-bottom: 110px;
}

.news-img{
  display: flex;
  flex-direction: column;
  align-items: end;
  gap: 10px;
}

.news-img > img{
  width: 100%;
  height: 610px;
  object-fit: cover;
  object-position: center;
  border-radius: 20px;
}

.news-text{
  margin: 0 auto;
  margin-top: 80px;
  width: max-content;
  max-width: 730px;
}

@media (max-width: 768px) {
  h2 {
    font-size: 28px;
  }
  .created-at{
    margin-bottom: 20px;
  }
  .news-img {
    gap: 5px;
  }
  .news-img > span {
    font-size: 12px;
  }
  .news-img > img{
    height: 160px;
  }
  .news-text{
    margin-top: 20px;
    max-width: 100%;
  }
  .news-content{
    margin-bottom: 55px;
  }
}
</style>
