<template>
  <div class="history-wrapper" id="history">
    <div class="container">
      <div class="img-block">
        <img src="/img/history.png" alt="">
      </div>
      <div class="content-block">
        <h3>История Молодежного бюро <br> 5 этаж</h3>
        <div class="content">
          <p>История История История ИсторияИстория История История История История История История История История История История История История История История История История История</p>
          <p>История История История ИсторияИстория История История История История История История История История История История История История История История История История История</p>
        </div>
        <RouterLink to=""><IconButton class="link-button" text="команды"><img src="/icon/white-arrow.svg" alt=""></IconButton></RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import IconButton from '@/components/UI/button/IconButton.vue';
</script>

<style scoped>
.history-wrapper{
  margin-top: 50px;
  margin-bottom: 120px;
}

.container{
  display: flex;
  gap: 70px;
  margin: 0 auto;
  max-width: 1800px;
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
  border-color: white;
  width: 100%;
  color: white;
}

.content > p{
  margin-top: 20px;
}
</style>
