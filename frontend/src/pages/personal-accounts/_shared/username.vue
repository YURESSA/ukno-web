<template>
  <div class="card-wrapper">
    <div class="avatar">
      <h2>Д</h2>
    </div>
    <div class="name">
      <h5>Гость</h5>
      <h3>Дмитрий Дмитрий Антонченко</h3>
    </div>
  </div>
</template>


<script setup>

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
  color: #F25C03;
}

h3{
  max-width: 500px;
  overflow: hidden;
  text-overflow: ellipsis
}
</style>
