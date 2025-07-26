<template>
  <div class="welcom-wrapper page--margin">
    <div class="title">
      <h1>Молодежное бюро</h1>
      <h2>5 этаж</h2>
    </div>
    <div class="welcom-img"></div>
    <p>Культурно-образовательный центр, где <br>
      история встречает современность, а творчество  <br>
      и  саморазвитие вдохновляют</p>
  </div>
</template>

<script setup>

</script>

<style scoped>
.welcom-wrapper{
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

h2{
  text-align: center;
}

p{
  font-size: 24px;
  text-align: center;
}

.welcom-img{
  content: '';
  width: 50%;
  height: 300px;
  border-radius: 50%;
  background-image: url('/img/welcom.png');
}
</style>
