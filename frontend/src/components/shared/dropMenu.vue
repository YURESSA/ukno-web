<template>
  <div class="drop-wrapper">
    <div class="drop-groups">
      <button class="close__button"><img src="/icon/filter/close.svg" alt="Закрыть" @click="emit('close')"></button>
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
const emit = defineEmits(['close']);

</script>

<style scoped>
.close__button{
  position: absolute;
  right: 25px;
  top: 20px;
  padding: 6px 6px;
  border-radius: 100%;
  background-color: #EDEDED8A;
}

.close__button:hover{
  background-color: #afaeae8a;
}

.close__button:active{
  background-color: #e7e4e4b7;
}

.drop-wrapper{
  position: fixed;
  bottom: -500px;
  opacity: 0;
  width: 100%;
  z-index: 1001;
  transition: all 0.5s ease;
}

.drop-groups {
  display: flex;
  flex-direction: column;
  position: relative;
  gap: 20px;
  padding: 15px;
  background: #fff;
  border-radius: 21px 21px 0 0;
  padding: 30px 24px 38px 24px;
}
</style>
