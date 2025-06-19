<template>
  <div class="header-wrapper">
    <h4>Запись на экскурсию «{{ title }}»</h4>
    <IconButton @click="closePage" class="close_btn"><img src="/icon/maki_cross.svg" alt=""></IconButton>
  </div>
</template>

<script setup>
import IconButton from '@/components/UI/button/IconButton.vue';
import { useRouter } from 'vue-router';

const router = useRouter(); // для Composition API

const props = defineProps({
  title: {
    type: String,
  }
});

function closePage(){
  console.log('History state:', window.history.state);
  console.log('History length:', window.history.length);
  router.back();
}
</script>

<style scoped>
.header-wrapper{
  display: flex;
  width: 100%;
  height: max-content;
  align-items: center;
  justify-content: flex-end;
  padding-bottom: 20px;
  border-bottom: 2px solid #7A797873;
}

h4{
  flex: 1;
  text-align: center;
  margin: 0;
}

.close_btn{
  width: 23px;
  height: 23px;
  padding: 4px;
  border-radius: 5px;
  border: none;
  background-color: #EDEDED8A;
}
</style>
