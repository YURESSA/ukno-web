<template>
  <div class="news-content">
    <div class="title">
      {{  }}
    </div>
    <div class="created-at">
      <span>{{  }} • УКНО: Сообщество на Урале</span>
    </div>
    <div class="news-img">
      <img src="" alt="">
      <span>Фото: {{  }}</span>
    </div>
    <div class="news-text">

    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  newsContent: Object,
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
</style>
