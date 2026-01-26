<!-- <template>
  <div class="container" v-if="news">
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
</template> -->

<template>
  <div class="title" id="news">
    <h3>Новости молодежного бюро</h3>
  </div>
  <div class="history-wrapper" id="history">
    <div class="container" v-if="news">
      <div class="img-block">
        <img :src="imageUrl" alt="">
      </div>
      <div class="content-block">
        <h3>{{ news[0].title }}</h3>
        <div class="content">
          <p>{{ news[0].short_description }}</p>
        </div>
        <RouterLink to="/news"><IconButton class="link-button" text="Открыть новость"><img src="/icon/white-arrow.svg" alt=""></IconButton></RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import IconButton from '@/components/UI/button/IconButton.vue';
import NewsCard from '@/components/shared/news-card.vue';
import { baseUrl } from '@/stores/counter';
import { computed } from 'vue';

const props = defineProps({
  news: Array,
})

const imageUrl = computed(() => baseUrl + props.news[0].images[0])
</script>

<style scoped>
.history-wrapper{
  margin-top: 56px;
  margin-bottom: 120px;
}

.title{
  width: 100%;
  max-width: 1800px;
}

.container{
  display: flex;
  gap: 70px;
  margin: 0 auto;
  max-width: 1800px;
}

.img-block > img {
  display: block;
  width: 310px;
  height: 430px;
  object-fit: cover;
  object-position: center;
  border-radius: 15px;
}

.content-block{
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: 100%;
}

.content{
  margin-top: 40px;
  margin-bottom: 60px;
}

.link-button{
  border: 1px solid white;
  width: 100%;
  color: white;
  background: none;
}

.link-button:hover {
  background-color: #4E4E4E;
}

.link-button:active {
  background-color: #949494;
}

.content > p{
  margin-top: 20px;
  max-width: 1000px;
}

@media (max-width: 756px) {
  .img-block > img {
    width: 100%;
    height: 167px;
    border-radius: 0px;
  }
  .container{
    display: flex;
    flex-direction: column;
    gap: 40px;
  }
  .content {
    margin: 30px 0;
  }
  .history-wrapper{
    margin-bottom: 40px;
  }
}
</style>

<!-- <script setup>
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
</style> -->
