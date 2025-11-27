<template>
  <div class="info-card-wrapper">
    <div class="card">
      <div class="angel"></div>
      <div class="title">
        <h3>{{ title }}</h3>
      </div>
      <div class="content">
        {{ content }}
      </div>
    </div>
  </div>
</template>

<script setup>

defineProps({
  title: String,
  content: String,
})
</script>

<style>

.info-card-wrapper{
  width: 283px;
  height: 356px;
}

.card{
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border: 2px solid #f25c03;
  border-radius: 14px;
  padding: 20px;
  max-width: 100%;
  height: calc(100% - 40px);
  backdrop-filter: blur(6px);
  background: rgba(255, 255, 255, 0.2);
  transition: all 0.7s ease;
  position: relative;
  overflow-x: hidden;
}

.angel{
  content: "";
  width: 200px;
  height: 200px;
  position: absolute;
  background-image: url('/public/about-us/icon/andels.svg');
  z-index: 99;
  background-repeat: no-repeat;
  right: -6px;
  top: 0px;
  opacity: 0;
  transition: all 0.7s ease;
}

.info-card-wrapper:hover .card {
  transform: translateY(60px);
  background-color: #FF6C36;
}


.info-card-wrapper:hover .angel {
  opacity: 1;
}

</style>
