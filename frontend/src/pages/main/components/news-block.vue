<template>
  <div class="container">
    <div class="title" id="news">
      <h3>Новости молодежного бюро</h3>
    </div>
    <div class="news-content">
      <template v-for="(item, index) in news.slice(0, 2)" :key="index">
        <NewsCard
          :title="item.title"
          :imageName="baseUrl + item.images[0]"
          :id = 'item.news_id'
        ></NewsCard>
      </template>

      <div
        class="half-width-container"
        v-if="news.length > 2"
      >
        <template v-for="(item, index) in news.slice(2, 4)" :key="index + 2">
          <NewsCard
            :title="item.title"
            :imageName="baseUrl + item.images[0]"
          ></NewsCard>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import NewsCard from '@/components/shared/news-card.vue';
import { baseUrl } from '@/stores/counter';

const props = defineProps({
  news: Object,
})
</script>

<style scoped>
.news-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
  margin-bottom: 90px;
  margin-top: 40px;
}

.container{
  margin: 0 auto;
  max-width: 1800px;
}

.half-width-container {
  display: flex;
  gap: 30px;
}

.half-width {
  flex: 1;
}
</style>
