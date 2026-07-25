<template>
  <div class="card-wrapper">
    <p class="text-l bold">Номер телефона</p>
    <div class="data-wrapper">
      <p class="text-l content">{{ phone }}</p> <!-- <IconButton class="edit__btn"><img src="/icon/pencil.svg" alt=""></IconButton> -->
    </div>
    <p class="text-l bold">Электронная почта</p>
    <div class="data-wrapper">
      <p class="text-l content">{{ email }}</p> <!-- <IconButton class="edit__btn"><img src="/icon/pencil.svg" alt=""></IconButton> -->
    </div>
    <p class="text-l bold">Пароль</p>
    <div class="password-data-wrapper">
      <DefaultButton class="change__btn text-l" text="Сменить пароль" @click="$emit('open')"></DefaultButton>
    </div>
  </div>
</template>


<script setup>
import IconButton from '@/components/ui/button/IconButton.vue';
import DefaultButton from '@/components/ui/button/DefaultButton.vue';

const props = defineProps({
  email: String,
  phone: String
})
</script>

<style scoped>
.card-wrapper{
  display: flex;
  flex-direction: column;
  justify-content: center;
  max-height: max-content;
  padding: 50px 77px;

  width: calc(100% - 77*2px);
  border-radius: 26px;
  box-shadow: 0px 0px 12.7px 0px #0000002E;
}

.data-wrapper{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.password-data-wrapper{
  margin-top: 10px;
}

.edit__btn{
  border: none;
  padding: 10px;
  border-radius: 100%;
}

.change__btn{
  padding: 10px 30px;
  background-color: #ECEDF1;
  font-size: 20px;
  border-radius: 30px;
}

@media (max-width: 768px) {
  .card-wrapper{
    padding: 0;
    width: 100%;
    box-shadow: none;
  }
  .text-l {
    font-size: 16px;
  }
  .content{
    font-size: 16px;
    color: #989898;
  }
}
</style>
