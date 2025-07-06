<template>
  <div class="card-wrapper">
    <h5>Номер телефона</h5>
    <div class="data-wrapper">
      <p>{{ phone }}</p> <!-- <IconButton class="edit__btn"><img src="/icon/pencil.svg" alt=""></IconButton> -->
    </div>
    <h5>Электронная почта</h5>
    <div class="data-wrapper">
      <p>{{ email }}</p> <!-- <IconButton class="edit__btn"><img src="/icon/pencil.svg" alt=""></IconButton> -->
    </div>
    <h5>Пароль</h5>
    <div class="password-data-wrapper">
      <DefaultButton class="change__btn" text="Сменить пароль" @click="$emit('open')"></DefaultButton>
    </div>
  </div>
</template>


<script setup>
import IconButton from '@/components/UI/button/IconButton.vue';
import DefaultButton from '@/components/UI/button/DefaultButton.vue';

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
</style>
