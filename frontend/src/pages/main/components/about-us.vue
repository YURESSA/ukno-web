<template>
  <div class="page-wrapper" id="about">
    <div class="container text-medium" v-if="!$isMobile()">
      <div class="design-img">
        <!-- <img class="absolut--img left-ear" src="/icon/main/leftEar.png" alt=""> -->
        <!-- <img class="absolut--img bottom-ear" src="/icon/main/bottomEar.png" alt=""> -->
      </div>
      <div class="title">
        <h3>Юра лох ):)</h3>
        <img class="absolut--img flower-big" src="/icon/main/flower-big.png" alt="">
      </div>
      <div class="about-content">
        <div class="content-wrapper">
          <div class="content right-border">
            <p> Резиденты кластера «Хлебзавод №6» вместе с другими участниками проводим экскурсии и создаем  пространство для  креативных идей, вдохновения и развития</p>
          </div>
          <div class="content">
            <img class="absolut--img flower-small" src="/icon/main/flower-small.png" alt="">
            <p>Мы находимся на территории бывшего <br>
              хлебозавода №6, который работал с 1978 года. <br>
              Сегодня мы сохраняем дух прошлого, создавая <br> новое будущее.</p>
          </div>
        </div>
        <div class="content-wrapper">
          <div class="content">
            <!-- <img class="absolut--img mouse" src="/icon/main/mouse.png" alt=""> -->
            <img class="absolut--img ear" src="/icon/main/ear.png" alt="">
          </div>
          <div class="content border">
            <p>С 2025 года мы открыли новое <br> пространство для молодежных инициатив, <br> образовательных мероприятий и <br> творческих проектов.</p>
          </div>
          <div class="content">
            <img class="absolut--img bread" src="/icon/main/bread1.png" alt="">
          </div>
        </div>
      </div>
      <UsResult></UsResult>
    </div>

    <div class="mobile-about-us" v-if="$isMobile()">
      <div class="title">
        <h2>Кто мы такие?</h2>
      </div>
      <div
        class="content-list"
        ref="slider"
        @touchstart="pauseAutoScroll"
        @mousedown="pauseAutoScroll"
        @wheel="pauseAutoScroll"
      >
        <div class="about-card" v-for="(item, i) in cards" :key="i">
          <p>{{ item }}</p>
        </div>

        <div class="about-card" v-for="(item, i) in cards" :key="'clone-' + i">
          <p>{{ item }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import UsResult from './us-result.vue';
import { ref, onMounted, onBeforeUnmount } from 'vue'

const slider = ref(null)

const cards = [
  'Резиденты кластера «Хлебзавод №6» вместе с другими участниками проводим экскурсии и создаем пространство для креативных идей, вдохновения и развития',
  'Мы находимся на территории бывшего хлебозавода №6, который работал с 1978 года. Сегодня мы сохраняем дух прошлого, создавая новое будущее',
  'С 2025 года мы открыли новое пространство для молодежных инициатив, образовательных мероприятий и творческих проектов'
]

let position = 0
let speed = 0.4
let isPaused = false
let animationId = null
let resumeTimeout = null

const autoScroll = () => {
  if (!slider.value) return

  if (!isPaused) {
    position += speed
    slider.value.scrollLeft = position
  }

  if (position >= slider.value.scrollWidth / 2) {
    position = 0
    slider.value.scrollLeft = 0
  }

  animationId = requestAnimationFrame(autoScroll)
}

const pauseAutoScroll = () => {
  isPaused = true
  clearTimeout(resumeTimeout)

  resumeTimeout = setTimeout(() => {
    position = slider.value.scrollLeft
    isPaused = false
  }, 2000)
}

onMounted(() => {
  animationId = requestAnimationFrame(autoScroll)
})

onBeforeUnmount(() => {
  cancelAnimationFrame(animationId)
  clearTimeout(resumeTimeout)
})

</script>

<style scoped>
.page-wrapper{
  background-color: #FFD6BD;
  padding: 24px 0 48px 0;
  padding-bottom: 0px;
  height: calc(100% + 150px);
}

.title{
  position: relative;
  text-align: center;
}

.absolut--img{
  position: absolute;
  pointer-events: none;
}

.ear{
  bottom: -200px;
  right: 0;
  transform: rotate(-30deg) scaleX(-1);

}

.flower-big{
  top: -130px;
  right: 10px;
}

.flower-small{
  bottom: 0px;
  right: 20px;
}

.bread{
  bottom: -250px;
  left: -120px;
}

/* .left-ear{
  z-index: -1;
  left: 0px;
}

.bottom-ear{
  z-index: -1;
  bottom: -230px;
} */

.container{
  margin: 0 auto;
  max-width: 1800px;
}

.about-content{
  margin-top: 40px;
  margin-bottom: 120px;
}

.content-wrapper{
  display: flex;
  width: 100%;
  border-top: 1px solid white;
}

.content-wrapper > .content{
  display: flex;
  align-items: center;
  text-align: left;
  width: 50%;
  height: 220px;
  padding-left: 30px;
  position: relative;
}

.content > p{
  max-width: 485px;
}

.right-border{
  display: flex;
  justify-content: flex-end;
  border-right: 1px solid white;
}

.right-border > p{
  text-align: right;
  margin-right: 45px;
}

.border{
  justify-content: center;
  border-right: 1px solid white;
  border-left: 1px solid white;
}

.border > p {
  text-align: center;
}


.content-list {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  gap: 20px;
  overflow-x: scroll;
  scrollbar-width: none;
  -ms-overflow-style: none;
  scroll-behavior: auto;
}

.content-list::-webkit-scrollbar {
  display: none;
}

.about-card {
  width: 286px;
  height: 129px;
  padding: 22px;
  text-align: left;
  border: 1px solid white;
  flex-shrink: 0;
}

.about-card > p {
  width: 100%;
  font-weight: 500;
  font-size: 16px;
  line-height: 140%;
  color: #333;
}

.mobile-about-us > .title > h2 {
  margin-left: 24px;
  margin-bottom: 28px;
  text-align: left;
}

@media (max-width: 768px) {
  .page-wrapper{
    padding-bottom: 48px;
  }
}
</style>
