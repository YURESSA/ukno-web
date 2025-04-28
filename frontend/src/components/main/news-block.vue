<template>
  <div class="title" id="news">
    <h3>Новости молодежного бюро</h3>
  </div>
  <div class="news-content">
    <NewsCard title="ПРОГРЕСС-24" imageName="news-img.png"></NewsCard>
    <NewsCard title="ПРОГРЕСС-24" imageName="news-img4.png"></NewsCard>
    <div class="half-width-container">
      <NewsCard title="ПРОГРЕСС-24" imageName="news-img3.png" class="half-width"></NewsCard>
      <NewsCard title="ПРОГРЕСС-24" imageName="news-img2.png" class="half-width"></NewsCard>
    </div>
  </div>
</template>

<script setup>
import NewsCard from '../UI/news-card.vue';
</script>

<style scoped>
.news-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
  margin-bottom: 90px;
  margin-top: 40px;
}

.half-width-container {
  display: flex;
  gap: 30px;
}

.half-width {
  flex: 1;
}
</style>
