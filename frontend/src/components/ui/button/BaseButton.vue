<template>
  <button>{{ text }}</button>
</template>

<script setup>
defineProps({
  text: String,
})
</script>

<style scoped>
button{
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  width: 226;
  height: 45;
  border-radius: 15px;
  padding: 10px 50px;
  background: #F25C03;
  color: #FFFFFF;
  font-weight: 400;
  font-size: 20px;
}

button:hover{
  background: #cf5006;
}

button:active{
  background-color: #c96a33;
}
</style>
