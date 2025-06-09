<template>
  <div
  class="card"
  :style="{ backgroundImage: `url(/img/${imageName})` }"
  >
    <p>{{ title }}</p>
    <RouterLink to="">
      узнать подробнее<img src="/icon/white-arrow.svg" alt="">
    </RouterLink>
  </div>
</template>

<script setup>
defineProps({
  imageName: String,
  title: String,
})
</script>

<style scoped>
.card{
  height: 180px;
  display: flex;
  justify-content: space-between;
  background-size: 100%;
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
