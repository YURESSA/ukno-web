<template>
  <button><slot>a</slot></button>
</template>

<script setup>

</script>

<style scoped>
button{
  all: unset;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  transition: all 0.3s ease;
  border-radius: 100%;
  height: max-content;
}

button:active {
  background-color: rgb(190, 190, 190);
}
</style>
