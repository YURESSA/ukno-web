<template>
  <div class="card-wrapper">
    <div class="avatar">
      <h2>{{ firstLetter.toUpperCase() }}</h2>
    </div>
    <div class="name">
      <h5>{{ roleName }}</h5>
      <h3>{{ full_name }}</h3>
    </div>
  </div>
</template>


<script setup>
import { computed } from 'vue'

const props = defineProps({
  role: String,
  full_name: String
})

const roleName = computed(() => {
  switch (props.role) {
    case 'user':
      return 'Гость'
    case 'admin':
      return 'Администратор'
    case 'resident':
      return 'Резидент'
    default:
      return 'Неизвестная роль'
  }
})

const firstLetter = computed(() => props.full_name?.[0] ?? '')

</script>

<style scoped>
.card-wrapper{
  display: flex;
  justify-content: center;
  align-items: center;
  max-height: max-content;
  gap: 45px;
  padding: 35px 125px;

  width: 570px;
  border-radius: 26px;
  box-shadow: 0px 0px 12.7px 0px #0000002E;
}

.avatar{
  display: flex;
  justify-content: center;
  align-items: center;
  height: 115px;
  min-width: 115px;
  border-radius: 100%;
  background-color: #FFD6BD;
}

.avatar > h2{
  color: #F25C03!important;
}

h3{
  max-width: 500px;
  overflow: hidden;
  text-overflow: ellipsis
}
</style>
