<template>
  <div class="container">
    <h3>Партнёры</h3>
    <div class="partners-block">
      <img src="/logo/ukno.svg" alt="">
      <img src="/logo/ПФКИ_Лого.svg" alt="">
      <img src="/logo/Хлебозавод_логотип.svg" alt="">
      <img src="/logo/Фудфейс_логотип.svg" alt="">
    </div>
    <div class="partners-block">
      <img src="/logo/5.svg" alt="">
      <img src="/logo/6.svg" alt="">
      <img src="/logo/7.svg" alt="">
      <img src="/logo/8.svg" alt="">
    </div>
    <div class="partners-block">
      <img src="/logo/12.svg" alt="">
      <img src="/logo/10.svg" alt="">
      <img src="/logo/12.svg" alt="">
      <img src="/logo/12.svg" alt="">
    </div>
  </div>
</template>

<script setup>

</script>

<style scoped>
.partners-block{
  display: flex;
  justify-content: space-around;
  border-radius: 36px;
  padding: 45px 0;
}

.partners-block > img{
  width: 241px;
  height: 88px;
}

.container{
  margin: 0 auto;
  max-width: 1800px;
}

h3{
  margin-bottom: 30px;
}
</style>
