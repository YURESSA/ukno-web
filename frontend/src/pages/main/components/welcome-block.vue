<template>
  <div class="content">
    <div class="h">Молодежное бюро</div>
    <h1 class="intro-text">
      Культурно-образовательный центр, где история встречает <br />
      современность, а творчество и саморазвитие вдохновляют
    </h1>
  </div>

  <div class="group">
    <div class="image"></div>
  </div>
</template>

<style scoped>
.content {
  position: relative;
  height: 78px;
  font-family: Helvetica, sans-serif;
  overflow: visible;
  z-index: 2;
  padding-bottom: 10px;
}

.group {
  position: relative;
  width: 100%; /* вместо 100vw */
  height: 790px;
  overflow: hidden;
  z-index: 1;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.group .image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%; /* вместо 100vw */
  height: 790px;
  background-image: url('/img/welcome.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: -1;
  border-radius: 29px;
  box-sizing: border-box;
}

.h {
  position: absolute;
  top: 0;
  left: 30px;
  font-family: 'Carabine-Medium', Helvetica, sans-serif;
  font-size: 77.8px;
  font-weight: 500;
  letter-spacing: -5.44px;
  line-height: 77.8px;
  color: #ff6c36;
  white-space: nowrap;
  user-select: none;
  z-index: 3;
}

.intro-text {
  position: absolute;
  top: 18px;
  right: 50px;
  max-width: 471px;
  font-family: 'Manrope-Medium', Helvetica, sans-serif;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 0;
  line-height: 22.4px;
  text-align: left;
  color: #333333;
  margin: 0;
  z-index: 3;
}
</style>
<script setup lang="ts"></script>
