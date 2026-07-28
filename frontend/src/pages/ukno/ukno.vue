<template>
  <div class="page-wrapper page--margin">
    <span><RouterLink to="/">Главная</RouterLink> / О нас</span>

    <div class="about-us">
      <div class="title">
        <h2 v-if="!$isMobile()">Молодёжное бюро <br> 5 этаж</h2>
        <h2 v-if="$isMobile()">Молодёжное <br>  бюро</h2>
        <img src="/about-us/young-buro.png" class="team-img" alt="">
      </div>
      <div class="who-we">
        <img src="/about-us/IMG_7642 2.png" alt="">
        <h3 class="text-orange">Кто мы</h3>
        <p>Мы - команда Уральского клуба нового образования — живое сообщество педагогов, психологов, инженеров и самих подростков, которые вместе создают образование будущего. Не лекции и учебники, а реальные проекты, эксперименты и осмысленное общение.</p>
      </div>
    </div>

    <div class="why-trust">
      <div class="ear" v-if="!$isMobile()"></div>
      <div class="left-ear" v-if="!$isMobile()"></div>
      <div class="title">
        <h3>Почему нам  <br> можно <span class="text-orange">доверять</span></h3>
        <p>Мы не просто говорим об изменениях в образовании — мы их создаём каждый день.</p>
      </div>
      <div class="info-card" v-if="!$isMobile()">
        <Card :title="'75+'" :content="'75+ партнёров — школы, вузы, технологические компании'"/>
        <Card :title="'31'" :content="'31 год опыта — работаем с 1994 года'"/>
        <Card :title="'8'" :content="'8 авторских программ — от робототехники до 3D-моделирования'"/>
        <Card :title="'18'" :content="'18 наставников прошли обучение в Сколково'"/>
      </div>
      <div class="info-mobile-card" v-if="$isMobile()">
        <div class="card-mobile">
          <div class="title">
            <h3>75+</h3>
          </div>
          <div class="content">
            <p>75+ партнёров — школы, вузы, технологические компании</p>
          </div>
          <img src="/about-us/icon/mobile-wave.svg" class="wave-mobile" alt="">
        </div>

        <div class="card-mobile card-mobile--orange">
          <div class="title">
            <h3>31</h3>
          </div>
          <div class="content">
            <p>31 год опыта — работаем с 1994 года</p>
          </div>
          <img src="/about-us/icon/mobile-union.svg" class="union-mobile" alt="">
        </div>

        <div class="card-mobile">
          <div class="title">
            <h3>8</h3>
          </div>
          <div class="content">
            <p>8 авторских программ — от робототехники до 3D-моделирования</p>
          </div>
          <img src="/about-us/icon/mobile-circles.svg" class="circle-mobile" alt="">
        </div>

        <div class="card-mobile card-mobile--orange">
          <div class="title">
            <h3>18</h3>
          </div>
          <div class="content">
            <p>18 наставников прошли обучение в Сколково</p>
          </div>
          <img src="/about-us/icon/mobile-leaf.svg" class="leaf-mobile-left" alt="">
          <img src="/about-us/icon/mobile-leaf.svg" class="leaf-mobile-right" alt="">
        </div>
      </div>
    </div>

    <div class="what-we-do">
      <div class="title">
        <h3>Мы делаем не только бюро, а ещё:</h3>
      </div>
      <div class="info-block">
        <div class="teenager age-block">
          <div class="book" v-if="!$isMobile()"></div>
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
        <h3 v-if="!$isMobile()">У нас очень <span class="custom-text">классная</span> команда. Знакомьтесь!</h3>
        <h3>Наша команда</h3>
      </div>
      <div class="person-list">
        <div class="person-card" v-for="(k, index) in teams" :key="k.id">
          <img :class="{'uneven-person': teams.length % 2 && index === teams.length - 1}" :src="baseUrl + k.photo" alt="">
          <p class="name">{{ k.full_name }}</p>
          <div class="profession" v-html="k.description"></div>
        </div>
      </div>
    </div>
    <h2 v-if="$isMobile()">Наши ценности</h2>
    <div class="advantages">
      <div class="first advantages-item">
        <h3 class="step">01</h3>
        <div class="advantages-content">
          <h3 class="advantages-name">Равенство</h3>
          <p>У нас нет "учителей" и "учеников", есть партнёры по проектам.</p>
        </div>
      </div>
      <div class="second advantages-item">
        <h3 class="step">02</h3>
        <div class="advantages-content">
          <h3 class="advantages-name">Действие</h3>
          <p>Не ждём изменений, а создаём их.</p>
        </div>
      </div>
      <div class="third advantages-item">
        <h3 class="step">03</h3>
        <div class="advantages-content">
          <h3 class="advantages-name">Развитие без <br> остановки</h3>
          <p>Сами постоянно учимся и вдохновляем других.</p>
        </div>
      </div>
      <div class="fourth advantages-item">
        <h3 class="step">04</h3>
        <div class="advantages-content">
          <h3 class="advantages-name">Безопасная среда</h3>
          <p>Можно ошибаться, спорить, пробовать новое.</p>
        </div>
      </div>
      <div class="five advantages-item">
        <h3 class="step">05</h3>
        <div class="advantages-content">
          <h3 class="advantages-name">Настоящие задачи</h3>
          <p>Работаем с реальными кейсами, а не учебными примерами.</p>
        </div>
      </div>
    </div>


    <div class="timeline">
      <h3>История нашего бюро</h3>
      <div class="timeline-wrapper" ref="timelineWrapper">
        <div class="line-bg">
          <div class="line-fill" :style="{ height: fillHeight + '%' }"></div>
        </div>
        <div
          v-for="(event, index) in sortHistory"
          :key="event.id"
          class="timeline-element"
        >
          <div class="dot"></div>
          <div
            class="info"
            :class="{

              'timeline-element-right': $isMobile(),
              'timeline-element-left': !$isMobile() && index % 2 === 1,
              'timeline-element-right': !$isMobile() && index % 2 === 0
            }"
          >
            <a v-if="event.link" :href="event.link" target="_blank"><p class="date text-l" v-html="formatDate(event.date)"></p></a>
            <a v-if="event.link" :href="event.link" target="_blank" class="event-info">
                <p class="text-l">{{ event.title }}</p>
                <p>{{ event.description }}</p>
            </a>
          </div>
        </div>
      </div>
    </div>

    <div class="more-info">
      <div class="vk-link">
        <h3 class="bold">Хотите узнать больше?</h3>
        <p>Присоединяйтесь к нам в Телеграмм и ВКонтакте</p>
        <div class="button-wrapper">
          <IconButton
            class="link--btn"
            text="Телеграмм"
            @click="openNewTab('https://t.me/buro5etag')"
          >
            <img src="/about-us/icon/arrow.svg" alt="">
          </IconButton>
          <IconButton
            class="link--btn"
            text="ВКонтакте"
            @click="openNewTab('https://vk.com/bureau5')"
          >
            <img src="/about-us/icon/arrow.svg" alt="">
          </IconButton>
        </div>
      </div>
      <div class="img-block" v-if="!$isMobile()">
        <div class="cirle"></div>
        <div class="flower"></div>
        <div class="big-book"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import IconButton from '@/components/ui/button/IconButton.vue';
import Card from '@/pages/ukno/components/card.vue';
import { ref, onMounted, onUnmounted, getCurrentInstance, computed  } from 'vue';
import { baseUrl, useDataStore } from '@/stores/counter';

const store = useDataStore();

const teams = computed(() => store.getTeamData);
const history = computed(() => store.getHistory);

const sortHistory = computed(() => {
  if(!history.value) {return}
  return [...history.value].sort((a, b) => a.date - b.date )
})

function formatDate(dateString) {
  const date = new Date(dateString);
  const day = date.getDate();
  const months = [
    'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
    'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
  ];
  const month = months[date.getMonth()];
  const year = date.getFullYear();

  return `${day} ${month}<br>${year}`;
}

const openNewTab = (url) => {
  window.open(url, '_blank', 'noopener,noreferrer');
};

const instance = getCurrentInstance()
const fillHeight = ref(0)
const timelineWrapper = ref(null)
const isMobile = instance?.appContext.config.globalProperties.$isMobile
const mobileMode = isMobile ? isMobile() : false

const updateTimeline = () => {
  const wrapper = timelineWrapper.value
  if (!wrapper) return

  const rect = wrapper.getBoundingClientRect()
  const windowHeight = window.innerHeight
  var start = null
  if (mobileMode) {
    start = windowHeight * 0.75
  } else {
    start = windowHeight * 0.75
  }
  const progress = (start - rect.top) / rect.height
  const percent = Math.min(Math.max(progress * 100, 0), 100)

  fillHeight.value = percent

  const dots = wrapper.querySelectorAll('.dot')
  const elements = wrapper.querySelectorAll('.timeline-element')
  const contentElements = wrapper.querySelectorAll('.info')

  dots.forEach((dot, index) => {
    const dotRect = dot.getBoundingClientRect()
    const dotTrigger = windowHeight * 0.75

    if (dotRect.top < dotTrigger) {
      dot.classList.add('active')
      elements[index]?.classList.add('active')
      if (mobileMode) {
        contentElements[index]?.classList.add('active-mobile')
      }
    } else {
      dot.classList.remove('active')
      elements[index]?.classList.remove('active')
      contentElements[index]?.classList.remove('active-mobile')
    }
  })
}

onMounted(async () => {
  await store.FetchTeam();
  await store.FetchHistory();
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

.team-img{
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
  justify-content: space-between;
  width: 234px;
  padding: 20px;
  border-radius: 14px;
  border: 2px solid #F25C03;
}

.person-card > img {
  display: block;
  width: 100%;
  border-radius: 14px;
  height: 260px;
  object-fit: cover;
}

.name {
  font-weight: bold;
  margin-top: 20px;
  margin-bottom: 10px;
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
  transition: all 0.3s ease;
}

.timeline-element.active {
  filter: saturate(1) brightness(1);
}

.info.active-mobile{
  margin-left: -109px;
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
  font-weight: 600;
}

.timeline-element-left > .date {
  text-align: end;
  padding: 20px 20px 30px 60px;
}

.event-info {
  display: block;
  position: absolute;
  padding: 30px 30px 40px 30px;
  width: max-content;
  max-width: 430px;
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
  width: calc(100% - 30px);
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

.button-wrapper {
  display: flex;
  gap: 15px;
}

.link--btn{
  width: 100%;
  margin-top: 30px;
  border: 2px solid #f25c03;
  border-radius: 14px;
  padding: 15px 17px;
  color: #333333;
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

@media (max-width: 768px) {
  .about-us{
    flex-wrap: wrap;
    gap: 0px;
    margin-bottom: 40px;
  }

  .what-we-do>.title {
    margin-bottom: 30px;
  }

  .about-us > .title > h2 {
    font-size: 40px;
  }
  .team-img{
    width: 100%;
    max-height: 190px;
    transform: translateY(-20px);
  }
  .who-we {
    padding-top: 20px;
  }
  .who-we > img {
    display: none;
  }
  .who-we > p{
    text-align: justify;
  }
  .why-trust{
    margin-bottom: 40px;
  }
  .why-trust > .title {
    flex-wrap: wrap;
    gap: 30px;
  }
  .parents, .teenager {
    padding: 24px;
    height: max-content;
  }
  .teenager > h3 {
    margin: 0;
  }
  .parents > .circle {
    width: 226px;
    height: 226px;
    background-size: contain;
    bottom: -55px;
    right: -40px;
    z-index: 1;
  }
  .parents > h3, .parents > p {
    z-index: 2;
    margin: 0;
  }

  .what-we-do{
    margin-bottom: 40px;
  }

  .what-we-do > .info-block {
    flex-wrap: wrap;
  }

  .person-list {
    gap: 24px;
    margin-top: 35px;
  }

  .person-card {
    flex: 1;
    padding: 11px;
  }

  .person-card > img {
    display: block;
    width: 100%;
    height: 150px;
  }

  .uneven-person {
    height: 250px!important;
  }

  .team {
    margin-bottom: 40px;
  }

  .advantages {
    width: 100vw;
    margin-left: -24px;
    margin-top: 30px;
    margin-bottom: 0px;
    border-radius: 14px;
  }
  .advantages-item{
    padding-top: 24px;
    padding-left: 24px;
    padding-right: 24px;
    align-items: flex-start;
    border-radius: 14px 14px 0 0px;
  }
  .advantages-item:last-of-type{
    padding-bottom: 84px;
  }
  .advantages-content {
    max-width: fit-content;
  }
  .advantages-content > h3 {
    margin: 0;
    margin-bottom: 20px;
    min-width: auto;
    max-width: max-content;
  }
  .step{
    margin-right: 24px;
  }

  .timeline {
    gap: 30px;
    margin-bottom: 260px;
  }

  .timeline-wrapper {
    gap: 269px;
  }

  .line-bg, .dot{
    left: 1px;
  }

  .info {
    transition: all 0.3s ease;
  }

  .timeline-element-right {
    margin: 0;
    margin-left: 1000px;
    margin-top: -90px;
  }

  .date {
    padding: 10px;
    padding-right: 38px;
    font-size: 16px;
  }
  .event-info {
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-width: 221px;
    padding: 10px;
    padding-bottom: 24px;
    top: 42px!important;
    left: 49px!important;
  }
  .event-info > .text-l {
    font-size: 16px;
    font-weight: 600;
  }
  .more-info{
    all: unset;
  }
  .vk-link {
    width: 100%;
  }
  .vk-link > p {
    width: 290px;
  }
  .button-wrapper {
    flex-direction: column;
    gap: 10px;
    margin-top: 30px;
  }
  .link--btn {
    font-size: 16px;
    margin-top: 0px;
  }
  .link--btn:hover {
    background: white;
  }
}

.info-mobile-card{
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-top: 20px;
}

.card-mobile {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 131px;
  align-items: flex-start;
  justify-content: space-between;
  padding: 24px;
  overflow: hidden;
  padding-bottom: 20px;
  border-radius: 14px;
  border: 2px solid #f25c03;
}

.card-mobile > .title, .card-mobile > .content{
  z-index: 2;
}

.card-mobile--orange {
  background-color: #FF6C36;
  color: white;
}

.wave-mobile{
  position: absolute;
  top: 0;
  right: 0;
  height: 100%;
  z-index: 1;
}

.union-mobile{
  position: absolute;
  top: 0;
  right: 0;
  height: 100%;
  z-index: 1;
}

.circle-mobile{
  position: absolute;
  top: 0;
  right: 0;
  height: 100%;
  z-index: 1;
}

.leaf-mobile-left {
  position: absolute;
  bottom: 0;
  right: 80px;
  z-index: 1;
}

.leaf-mobile-right {
  position: absolute;
  bottom: 0;
  right: -15px;
  z-index: 1;
  transform: scaleX(-1);
}

</style>
