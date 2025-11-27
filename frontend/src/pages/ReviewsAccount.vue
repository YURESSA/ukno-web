<template>
  <div class="page-wrapper">
    <div class="header">
      <iconBtn><img src='../../public/assets/icon/icon-arrow-black.svg'></iconBtn>
      <h1>Отзывы</h1>
    </div>
    <ul>
      <reviewAccountCard></reviewAccountCard>
      <reviewAccountCard></reviewAccountCard>
      <reviewAccountCard></reviewAccountCard>
    </ul>
  </div>

</template>

<script setup>
import reviewAccountCard from '@/components/shared/reviewAccountCard.vue';
import iconBtn from '@/components/ui/icon-btn.vue';
</script>

<style scoped>
.page-wrapper {
  display: flex;
  flex-direction: column;
  flex-direction: 14px;
}
ul{
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.header {
  display: flex;

}
.header button {
  padding-top: 10px;
}
h1{
  text-align: center;
  width: 100%;
}
</style>
