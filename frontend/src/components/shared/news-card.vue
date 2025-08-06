<template>
  <div
  class="card"
  :style="{ backgroundImage: `url(${imageName})` }"
  >
    <p>{{ title }}</p>
    <RouterLink :to="{ path: '/news', hash: `#news-${id}` }">
      узнать подробнее<img src="/icon/white-arrow.svg" alt="">
    </RouterLink>
  </div>
</template>

<script setup>
defineProps({
  imageName: String,
  title: String,
  id: String,
})
</script>

<style scoped>
.card{
  height: 180px;
  display: flex;
  justify-content: space-between;
  background-size: 100%;
  background-position: center;
  /* background-repeat: repeat; */
  /* либо contain & round */
  align-items: end;
  color: white;
  padding: 20px;
}

a{
  color: white;
}

img{
  margin-left: 10px;
}
</style>
