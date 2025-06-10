<template>
  <h5>Ближайшие события</h5>
  <div class="card-wrapper">
    <h5>Город без фильтров</h5>
    <p>Нескучный гид по настоящему городу</p>
    <p>25.05 | 14:00 |  Старт у фонтана</p>
  </div>
</template>


<script setup>

</script>

<style scoped>
.card-wrapper{
  display: flex;
  flex-direction: column;
  justify-content: center;
  max-height: max-content;
  gap: 20px;
  padding: 40px;

  width: 300px;
  border-radius: 14px;
  border: 1px solid #DEDEDE;
  margin-bottom: 10px;
}

p{
  margin-bottom: 10px;
}
</style>
