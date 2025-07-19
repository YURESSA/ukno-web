<template>
  <div class="page-wrapper" id="events">
    <div class="container">
      <div class="title">
        <h3>Мероприятия, <br>
          <span>которые вдохновляют, создают и объединяют</span></h3>
      </div>
      <div class="events-list">
      </div>
      <IconButton class="button" text="записаться"><img src="/icon/arrow.svg" alt=""></IconButton>
    </div>
  </div>
</template>

<script setup>
import IconButton from '@/components/UI/button/IconButton.vue';
</script>

<style scoped>
span{
  color: #F25C03;
}

.button{
  width: 100%;
}

.container{
  margin: 0 auto;
  max-width: 1800px;
}
</style>
