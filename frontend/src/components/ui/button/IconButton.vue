<template>
  <button>
    <span class="text">{{ text }}</span>
    <span class="slot-content">
      <slot></slot>
    </span>
  </button>
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
  width: max-content;
  border-radius: 15px;
  padding: 15px 20px;
  color: #fff;
  font-size: 20px;
  background: #FF6C36;
}

button:hover{
  background: #DD5827;
}

button:active{
  background-color: #FFA280;
}

.text {
  flex-grow: 1;
  text-align: center;
}

.slot-content{
  max-width: max-content;
  max-height: max-content;
  display: flex;
  align-items: center;
}
</style>
