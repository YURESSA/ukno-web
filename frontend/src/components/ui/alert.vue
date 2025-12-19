<template>
  <div v-if="show" class="notification-overlay">
    <div class="block-wrapper">
      <div class="notification-wrapper" :class="notificationClass">
        <div class="notification-header">
          <img src="/icon/bell.svg" class="img" :class="imgClass" alt="">
        </div>
        <p>{{ message }}</p>
        <hr>
        <button @click="close">OK</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  message: {
    type: String,
    default: 'Произошла ошибка, попробуйте ещё раз'
  },
  type: {
    type: String,
    default: 'negative'
  }
})

const emit = defineEmits(['close'])

const notificationClass = computed(() => {
  return `notification-${props.type}`
})

const imgClass = computed(() => {
  return `img-${props.type}`
})

function close() {
  emit('close')
}
</script>

<style scoped>

.notification-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
}

.hidden {
  display: none !important;
}

.notification-wrapper{
  width: 520px;
  padding: 90px 30px 0px;
  border-radius: 54px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  position: relative;
}

.block-wrapper{
  position: fixed;
  top: 50px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999999999999;
}

.notification-negative{
  background-color: #1f1f1f;
  color: white;
}

.notification-positive{
  background-color: #FFECE0;
  color: black;
}

.img-positive{
  filter: invert(1);
}

.notification-header{
  height: 93px;
  width: 93px;
  border-radius: 100%;
  background-color: #FF6C36;
  display: flex;
  justify-content: center;
  align-items: center;
  position: absolute;
  top: -35px;
}

p{
  font-size: 24px;
  width: 480px;
  text-align: center;
  margin-bottom: 20px;
}

hr{
  background-color: white;
  width: 100%;
  margin: 0;
}

button{
  all: unset;
  font-size: 20px;
  margin: 20px 0px;
  width: 300px;
  border-radius: 15px;
  text-align: center;
  transition: all 0.25s ease;
  cursor: pointer;
}

button:hover{
  background-color: #c9c9c940;
}

@media (max-width: 768px) {
  .notification-wrapper{
    width: 250px;
    padding: 30px 15px 0px;
    border-radius: 34px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    position: relative;
  }

  p {
    font-size: 16px;
    margin-bottom: 10px;
  }

  .notification-header{
    height: 40px;
    width: 40px;
    top: -15px;
  }
  .notification-header > img{
    height: 20px;
    width: 20px;
  }
  button{
    all: unset;
    font-size: 14px;
    margin: 10px 0px;
    width: 300px;
    border-radius: 15px;
    text-align: center;
    transition: all 0.25s ease;
    cursor: pointer;
  }
}
</style>
