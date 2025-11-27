<template>
  <div class="page-wrapper page--margin">
    <span><RouterLink to="/">Главная</RouterLink> / О нас</span>

    <div class="about-us">
      <div class="title">
        <h2>Уральский клуб нового <br> образования</h2>
        <img src="/public/about-us/time-photo.jpg" alt="">
      </div>
      <div class="who-we">
        <img src="/public/about-us/IMG_7642 2.png" alt="">
        <h3 class="text-orange">Кто мы</h3>
        <p>Мы — живое сообщество педагогов, психологов, инженеров и самих подростков, которые вместе создают образование будущего. Не лекции и учебники, а реальные проекты, эксперименты и осмысленное общение.</p>
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

    <div class="what-we-do">
      <div class="title">
        <h3>Что именно мы <br> делаем</h3>
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
    <div class="principles">
      <h3>Наши принципы:</h3>
      <div class="parinciples-wrapper">
        <div class="principles-element">
          <div class="line"></div>
          <div class="title">
            <h3 class="text-orange">Равенство</h3>
          </div>
          <div class="info">
              <div class="dot dot-first"></div>
            <p>У нас нет "учителей" и "учеников", <br> есть партнёры по проектам.</p>
          </div>
        </div>
        <div class="principles-element">
          <div class="title">
            <h3 class="text-orange">Действие </h3>
          </div>
          <div class="info">
              <div class="dot dot-second"></div>
            <p>Не ждём изменений, а создаём их.</p>
          </div>
        </div>
        <div class="principles-element">
          <div class="title">
            <h3 class="text-orange">Развитие без <br> остановки</h3>
          </div>
          <div class="info">
              <div class="dot dot-third"></div>
            <p>Развитие без остановки</p>
          </div>
        </div>
        <div class="principles-element">
          <div class="title">
            <h3 class="text-orange">Безопасная среда</h3>
          </div>
          <div class="info">
              <div class="dot dot-fourth"></div>
            <p>Можно ошибаться, спорить, пробовать новое.</p>
          </div>
        </div>
        <div class="principles-element">
          <div class="title">
            <h3 class="text-orange">Настоящие задачи</h3>
          </div>
          <div class="info">
            <div class="dot dot-fifth"></div>
            <p>Работаем с реальными кейсами, а не учебными <br> примерами.</p>
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
import Card from '@/pages/ukno/components/card.vue'

const openNewTab = (url) => {
  window.open(url, '_blank', 'noopener,noreferrer');
};
</script>

<style scoped>

.page-wrapper{
  max-width: 1280px;
  margin: 0 auto;
}

.about-us{
  display: flex;
  gap: 30px;
  margin-bottom: 105px;
}

.about-us > .title > img{
  width: 800px;
  height: 420px;
  border-radius: 15px;
}

.who-we{
  padding-top: 30px;
}

.who-we > img{
  border-radius: 20px;
  margin-bottom: 30px;
}

.who-we > h3{
  margin-bottom: 30px;
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
}

.parents > h3{
  margin-bottom: 30px;
  color: white;
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

.principles{
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 110px;
}

.principles-element{
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.parinciples-wrapper{
  display: flex;
  flex-direction: column;
  gap: 110px;
  width: 100%;
  position: relative;
}

.line{
  position: absolute;
  width: 8px;
  height: 100%;
  top: 0px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #F25C03;
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

.dot-second{
  top: 172px;
}

.dot-third{
  top: 360px;
}

.dot-fourth{
  top: 550px;
}

.dot-fifth{
  top: 740px;
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
