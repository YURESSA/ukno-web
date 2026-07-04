<template>
  <button>{{ text }}</button>
</template>

<script setup>
defineProps({
  text: String || null,
})
</script>

<style scoped>
button{
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 15px;
  padding: 6px 6px;
  background-color: #EDEDED8A;
}

button:hover{
  background: #afaeae8a;
}

button:active{
  background-color: #e7e4e4b7;
}
</style>
