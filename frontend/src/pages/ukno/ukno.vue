<template>
  <div class="page-wrapper page--margin">
    <span><RouterLink to="/">Главная</RouterLink> / О нас</span>

    <div class="about-us">
      <div class="title">
        <h2>Молодёжное бюро <br> 5 этаж</h2>
        <img src="/public/about-us/young-buro.png" alt="">
      </div>
      <div class="who-we">
        <img src="/public/about-us/IMG_7642 2.png" alt="">
        <h3 class="text-orange">Кто мы</h3>
        <p>Мы - команда Уральского клуба нового образования — живое сообщество педагогов, психологов, инженеров и самих подростков, которые вместе создают образование будущего. Не лекции и учебники, а реальные проекты, эксперименты и осмысленное общение.</p>
      </div>
    </div>

    <div class="what-we-do">
      <div class="title">
        <h3>Мы делаем не только бюро, а ещё:</h3>
      </div>
      <div class="info-block">
        <div class="teenager age-block">
          <div class="book"></div>
          <h3 class="text-orange">Для подростков</h3>
          <p>Проектные школы с погружением в инженерию и IT</p>
          <p>Хакатоны и акселераторы технологических проектов</p>
          <p>Тренинги soft skills и профориентационные игры</p>
          <p>Клубные встречи с крутыми специалистами</p>
        </div>

        <div class="parents age-block">
          <div class="circle"></div>
          <h3>Для родителей и педагогов</h3>
          <p>Подкаст «Мама, я инженер» о современном образовании</p>
          <p>Программы наставничества</p>
          <p>Методическая поддержка</p>
        </div>
      </div>
    </div>

    <div class="team">
      <div class="title">
        <h3>У нас очень <span class="custom-text">классная</span> команда. Знакомьтесь!</h3>
      </div>
      <div class="person-list">
        <div class="person-card">
          <img src="/about-us/time-photo.png" alt="">
          <p class="name">Денис Борисович</p>
          <p class="profession">курирует организацию корпоративных мероприятий.</p>
        </div>
        <div class="person-card">
          <img src="/about-us/time-photo.png" alt="">
          <p class="name">Денис Борисович</p>
          <p class="profession">курирует организацию корпоративных мероприятий.</p>
        </div>
        <div class="person-card">
          <img src="/about-us/time-photo.png" alt="">
          <p class="name">Денис Борисович</p>
          <p class="profession">курирует организацию корпоративных мероприятий.</p>
        </div>
        <div class="person-card">
          <img src="/about-us/time-photo.png" alt="">
          <p class="name">Денис Борисович</p>
          <p class="profession">курирует организацию корпоративных мероприятий.</p>
        </div>
        <div class="person-card">
          <img src="/about-us/time-photo.png" alt="">
          <p class="name">Денис Борисович</p>
          <p class="profession">курирует организацию корпоративных мероприятий.</p>
        </div>
      </div>
    </div>

    <div class="advantages">
      <div class="first advantages-item">
        <h3 class="step">(01)</h3>
        <h3 class="advantages-name">Равенство</h3>
        <p>У нас нет "учителей" и "учеников", есть партнёры по проектам.</p>
      </div>
      <div class="second advantages-item">
        <h3 class="step">(02)</h3>
        <h3 class="advantages-name">Действие</h3>
        <p>Не ждём изменений, а создаём их.</p>
      </div>
      <div class="third advantages-item">
        <h3 class="step">(03)</h3>
        <h3 class="advantages-name">Развитие без <br> остановки</h3>
        <p>Сами постоянно учимся и вдохновляем других.</p>
      </div>
      <div class="fourth advantages-item">
        <h3 class="step">(04)</h3>
        <h3 class="advantages-name">Безопасная среда</h3>
        <p>Можно ошибаться, спорить, пробовать новое.</p>
      </div>
      <div class="five advantages-item">
        <h3 class="step">(05)</h3>
        <h3 class="advantages-name">Настоящие задачи</h3>
        <p>Работаем с реальными кейсами, а не учебными примерами.</p>
      </div>
    </div>

    <div class="why-trust">
      <div class="ear"></div>
      <div class="left-ear"></div>
      <div class="title">
        <h3>Почему нам  <br> можно <span class="text-orange">доверять</span></h3>
        <p>Мы не просто говорим об изменениях в образовании — мы их создаём каждый день.</p>
      </div>
      <div class="info-card">
        <Card :title="'75+'" :content="'75+ партнёров — школы, вузы, технологические компании'"/>
        <Card :title="'31'" :content="'31 год опыта — работаем с 1994 года'"/>
        <Card :title="'8'" :content="'8 авторских программ — от робототехники до 3D-моделирования'"/>
        <Card :title="'18'" :content="'18 наставников прошли обучение в Сколково'"/>
      </div>
    </div>

    <div class="timeline">
      <h3>История нашего бюро</h3>
      <div class="timeline-wrapper" ref="timelineWrapper">
        <div class="line-bg">
          <div class="line-fill" :style="{ height: fillHeight + '%' }"></div>
        </div>
        <div class="timeline-element">
          <div class="dot"></div>
          <div class="info timeline-element-right">
            <p class="date text-l">12 октября <br> 2025</p>
            <div class="event-info">
              <p class="text-l">Проведение экспедиции</p>
              <p>В ходе экспедиции был осуществлён сбор полевых данных и образцов в соответствии с поставленными научными задачами.</p>
            </div>
          </div>
        </div>
        <div class="timeline-element">
          <div class="dot"></div>
          <div class="info timeline-element-left">
            <p class="date text-l">12 октября <br> 2025</p>
            <div class="event-info">
              <p class="text-l">Проведение экспедиции</p>
              <p>В ходе экспедиции был осуществлён сбор полевых данных и образцов в соответствии с поставленными научными задачами.</p>
            </div>
          </div>
        </div>
        <div class="timeline-element">
          <div class="dot"></div>
          <div class="info timeline-element-right">
            <p class="date text-l">12 октября <br> 2025</p>
            <div class="event-info">
              <p class="text-l">Проведение экспедиции</p>
              <p>В ходе экспедиции был осуществлён сбор полевых данных и образцов в соответствии с поставленными научными задачами.</p>
            </div>
          </div>
        </div>
        <div class="timeline-element">
          <div class="dot"></div>
          <div class="info timeline-element-left">
            <p class="date text-l">12 октября <br> 2025</p>
            <div class="event-info">
              <p class="text-l">Проведение экспедиции</p>
              <p>В ходе экспедиции был осуществлён сбор полевых данных и образцов в соответствии с поставленными научными задачами.</p>
            </div>
          </div>
        </div>
        <div class="timeline-element">
          <div class="dot"></div>
          <div class="info timeline-element-right">
            <p class="date text-l">12 октября <br> 2025</p>
            <div class="event-info">
              <p class="text-l">Проведение экспедиции</p>
              <p>В ходе экспедиции был осуществлён сбор полевых данных и образцов в соответствии с поставленными научными задачами.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="more-info">
      <div class="vk-link">
        <h3 class="bold">Хотите узнать больше?</h3>
        <p>Присоединяйтесь к нам в ВКонтакте</p>
        <IconButton
          class="link--btn"
          text="Узнать больше"
          @click="openNewTab('https://vk.com/bureau5')"
        >
          <img src="/public/about-us/icon/arrow.svg" alt="">
        </IconButton>
      </div>
      <div class="img-block">
        <div class="cirle"></div>
        <div class="flower"></div>
        <div class="big-book"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import IconButton from '@/components/UI/button/IconButton.vue';
import Card from '@/pages/ukno/components/card.vue';
import { ref, onMounted, onUnmounted } from 'vue';

const openNewTab = (url) => {
  window.open(url, '_blank', 'noopener,noreferrer');
};

const fillHeight = ref(0)
const timelineWrapper = ref(null)

const updateTimeline = () => {
  const wrapper = timelineWrapper.value
  if (!wrapper) return

  const rect = wrapper.getBoundingClientRect()
  const windowHeight = window.innerHeight

  const start = windowHeight * 0.55
  const progress = (start - rect.top) / rect.height
  const percent = Math.min(Math.max(progress * 100, 0), 100)

  fillHeight.value = percent

  const dots = wrapper.querySelectorAll('.dot')
  const elements = wrapper.querySelectorAll('.timeline-element')

  dots.forEach((dot, index) => {
    const dotRect = dot.getBoundingClientRect()
    const dotTrigger = windowHeight * 0.55

    if (dotRect.top < dotTrigger) {
      dot.classList.add('active')
      elements[index]?.classList.add('active')
    } else {
      dot.classList.remove('active')
      elements[index]?.classList.remove('active')
    }
  })
}

onMounted(() => {
  window.addEventListener('scroll', updateTimeline)
  updateTimeline()
})

onUnmounted(() => {
  window.removeEventListener('scroll', updateTimeline)
})
</script>

<style scoped>

.page-wrapper{
  max-width: 1280px;
  margin: 0 auto;
}

.about-us{
  display: flex;
  gap: 30px;
  margin-bottom: 80px;
}

.about-us > .title > img{
  width: 800px;
  height: 420px;
  border-radius: 15px;
  transform: translateY(-40px);
}

.who-we{
  padding-top: 30px;
}

.who-we > img{
  border-radius: 20px;
  margin-bottom: 30px;
}

.team{
  width: 100%;
  margin-bottom: 100px;
}

.custom-text {
  display: inline-block;
  border-radius: 23px;
  padding: 4px 20px;
  background-color: #ff6c36;
  transform: rotate(-3deg);
  color: white;
}

.person-list {
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
  margin-top: 60px;
}

.person-card{
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  width: 242px;
  padding: 20px;
  border-radius: 14px;
  border: 2px solid #F25C03;
}

.name {
  font-weight: bold;
  margin-top: 20px;
}

.advantages{
  background-color: #FF6C36;
  border-radius: 45px;
  display: flex;
  flex-direction: column;
  color: white;
  height: max-content;
  margin-bottom: 100px;
}

.advantages-item {
  display: flex;
  align-items: center;
  margin-top: -110px;
  border-radius: 45px 45px 0 0px;
  padding: 70px 30px 180px 30px;
}

.first{
  margin-top: 0px;
}

.second{
  background-color: white;
  color: #333333;
}

.third{
  background-color: #333333;
}

.fourth{
  background: linear-gradient(41deg, #ffbda5 0%, #ff6c36 100%);
}

.five {
  background-color: white;
  color: #333333;
}

.step {
  margin-right: 180px;
}

.advantages-name{
  min-width: 380px;
  margin-right: 80px;
}

.why-trust{
  position: relative;
  margin-bottom: 200px;
}

.ear{
  content: '';
  width: 250px;
  height: 270px;
  position: absolute;
  background-image: url('/public/about-us/icon/ear.svg');
  background-repeat: no-repeat;
  top: 60px;
  right: 0px;
  z-index: -1;
}

.left-ear{
  content: '';
  width: 250px;
  height: 350px;
  position: absolute;
  background-image: url('/public/about-us/icon/left-ear.svg');
  background-repeat: no-repeat;
  bottom: -210px;
  left: -100px;
  z-index: -1;
}

.why-trust > .title{
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.why-trust > .title > p{
  width: 390px;
}

.info-card{
  display: flex;
  align-items: center;
  margin-top: 60px;
  margin-bottom: 200px;
  gap: 30px;
}

.what-we-do{
  margin-bottom: 200px;
}

.what-we-do > .title{
  margin-bottom: 60px;
}

.what-we-do > .info-block{
  display: flex;
  gap: 30px;
}

.teenager{
  display: flex;
  flex-direction: column;
  gap: 20px;
  border: 1px solid #f25c03;
  border-radius: 38px;
  padding: 57px 55px;
  width: 595px;
  height: 473px;
  backdrop-filter: blur(6px);
  background-color: rgba(255, 255, 255, 0.2);
}

.teenager > h3{
  margin-bottom: 30px;
}

.parents{
  display: flex;
  flex-direction: column;
  position: relative;
  gap: 20px;
  border-radius: 38px;
  width: 595px;
  height: 473px;
  background-color: #ff6c36;
  padding: 57px 55px;
  overflow: hidden;
  color: white;
}

.parents > h3{
  margin-bottom: 30px;
}

.book{
  content: '';
  width: 391px;
  height: 530px;
  position: absolute;
  background-image: url('/public/about-us/icon/book.svg');
  background-repeat: no-repeat;
  bottom: -175px;
  left: 0px;
  z-index: -1;
}

.circle{
  content: '';
  width: 391px;
  height: 390px;
  position: absolute;
  background-image: url('/public/about-us/icon/circle.svg');
  background-repeat: no-repeat;
  bottom: -100px;
  right: -100px;
  z-index: 1;
}

.timeline{
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 110px;
  margin-bottom: 310px;
}

.timeline-wrapper{
  display: flex;
  flex-direction: column;
  gap: 152px;
  width: 100%;
  position: relative;
}

.timeline-element{
  display: flex;
  align-items: center;
  width: 100%;
  position: relative;
  justify-content: center;
  filter: saturate(0.9) brightness(0.9);
  transition: filter 0.3s ease;
}

.timeline-element.active {
  filter: saturate(1) brightness(1);
}

/* .line{
  position: absolute;
  width: 8px;
  height: 100%;
  top: 0px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #F25C03;
} */

.line-bg {
  position: absolute;
  width: 8px;
  height: 100%;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  background-color: #fde4d6;
  overflow: hidden;
}

.line-fill {
  width: 100%;
  height: 0;
  background-color: #F25C03;
  transition: height 0.2s ease-out;
}

.dot{
  position: absolute;
  width: 32px;
  height: 32px;
  border-radius: 100%;
  top: 0px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #F25C03;
}

.dot {
  background-color: #fde4d6;
  transform: translateX(-50%) scale(0.7);
  transition: all 0.3s ease;
}

.dot.active {
  background-color: #F25C03;
  box-shadow: 0 0 20px rgba(242, 92, 3, 0.8);
  transform: translateX(-50%) scale(1);
}

.info {
  position: relative;
  display: flex;
  align-items: start;
  justify-content: flex-start;
  margin-top: -116px;
  transform: translateY(56px);
}

.timeline-element-right {
  margin-right: -260px;
}

.timeline-element-left {
  margin-left: -260px;
}

.date {
  min-width: max-content;
  padding: 20px 60px 30px 20px;
  border-radius: 25px;
  background-color: #F25C03;
  color: white;
}

.timeline-element-left > .date {
  text-align: end;
  padding: 20px 20px 30px 60px;
}

.event-info {
  position: absolute;
  padding: 30px 30px 40px 30px;
  width: max-content;
  max-width: 490px;
  border-radius: 30px;
  backdrop-filter: blur(20.399999618530273px);
  box-shadow: 0 5px 22px -6px rgba(172, 66, 3, 0.2);
  background: linear-gradient(176deg, rgba(255, 255, 255, 0.25) 0%, rgba(242, 92, 3, 0.25) 100%);
  z-index: 999;
}

.timeline-element-right > .event-info {
  top: 60px;
  left: 82px;
}

.timeline-element-left > .event-info {
  top: 60px;
  right: 82px;
}

.more-info{
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  height: 640px;
  border: 2px solid #ff6c36;
  border-radius: 38px;
  padding-left: 30px;
  margin-top: 200px;
}

.vk-link{
  width: 48%;
}

.vk-link > h3{
  margin-bottom: 10px;
}

.link--btn{
  width: 100%;
  margin-top: 30px;
  border: 2px solid #f25c03;
  border-radius: 14px;
  padding: 15px 17px;
  background-color: #fff;
  height: 53px;
}

.img-block{
  border-radius: 36px;
  height: 100%;
  background: #ff6c36;
  width: 48%;
  position: relative;
  overflow: hidden;
}

.cirle{
  content: '';
  width: 391px;
  height: 390px;
  position: absolute;
  background-image: url('/public/about-us/icon/circles-vk.svg');
  background-repeat: no-repeat;
  bottom: -145px;
  left: -75px;
}

.flower{
  content: '';
  width: 391px;
  height: 390px;
  position: absolute;
  background-image: url('/public/about-us/icon/flower-vk.svg');
  background-repeat: no-repeat;
  top: -21px;
  right: -60px;
}

.big-book{
  content: '';
  width: 470px;
  height: 500px;
  position: absolute;
  background-image: url('/public/about-us/icon/book-vk.svg');
  background-repeat: no-repeat;
  background-position: center;
  top: 50%;
  right: 50%;
  transform: translate(50%, -50%);
}
</style>
