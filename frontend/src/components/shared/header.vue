<template>
  <div class="header-wrapper">
    <nav class="desktop-nav-wrapper" v-if="!$isMobile()">
      <ul class="nav-list">
        <li class="project">
          Проекты
          <ul class="project-list">
            <li>Психологический клуб</li>
            <li>Репетиторский клуб</li>
            <li>Музейное пространство</li>
          </ul>
        </li>
        <li><RouterLink to="/events">События</RouterLink></li>
        <li>
          <div class="logo">
            <RouterLink to="/"><img src="/logo/logo.svg" alt=""></RouterLink>
          </div>
        </li>
        <li><RouterLink to="/news">Новости</RouterLink></li>
        <li><RouterLink :to="{ path: '/ukno'}" replace >О нас</RouterLink></li>
      </ul>
      <div class="profile">
        <RouterLink to="/login" v-if="hasToken">
          <button>
            <img src="/icon/header/profile-fill.svg" alt="">
          </button>
        </RouterLink>
        <RouterLink to="/profile" v-else-if="!hasToken && role === 'user'">
          <button>
            <h4>{{ profileData.full_name[0].toUpperCase() }}</h4>
          </button>
        </RouterLink>
        <RouterLink to="/resident-profile" v-else-if="!hasToken && role === 'resident'">
          <button>
            <h4>{{ profileData.full_name[0].toUpperCase() }}</h4>
          </button>
        </RouterLink>
        <RouterLink to="/admin-profile" v-else-if="!hasToken && role === 'admin'">
          <button>
            <h4>{{ profileData.full_name[0].toUpperCase() }}</h4>
          </button>
        </RouterLink>
      </div>
    </nav>



<!-- Мобилка -->
    <nav v-else class="mobile-nav">
      <div class="mobile-header">
        <button @click="menuOpen = !menuOpen" class="menu-btn">
          <img src="/icon/menu-icon.svg" alt="">
        </button>
        <div class="mobile-logo">
          <RouterLink to="/" class="router-main">
            <img src="/logo/mobile-logo.svg" alt="Логотип">
          </RouterLink>
        </div>
        <div class="mobile-profile">
          <RouterLink to="/login" v-if="hasToken">
            <button>
              <img src="/icon/header/profile-fill.svg" alt="">
            </button>
          </RouterLink>
          <RouterLink to="/profile" v-else-if="!hasToken && role === 'user'">
            <button>
              <span>{{ profileData.full_name[0].toUpperCase() }}</span>
            </button>
          </RouterLink>
          <RouterLink to="/resident-profile" v-else-if="!hasToken && role === 'resident'">
            <button>
              <span>{{ profileData.full_name[0].toUpperCase() }}</span>
            </button>
          </RouterLink>
          <RouterLink to="/admin-profile" v-else-if="!hasToken && role === 'admin'">
            <button>
              <h4>{{ profileData.full_name[0].toUpperCase() }}</h4>
            </button>
          </RouterLink>
        </div>
      </div>

      <!-- Анимированное меню с использованием Transition -->
      <Teleport to="body">
        <Transition name="menu-fade">
          <div v-if="menuOpen" class="mobile-overlay" @click.self="menuOpen = false">
            <div class="mobile-menu">
              <ul>
                <li>
                  <div @click="toggleProjects" class="project-toggle">
                    Проекты
                  </div>
                  <Transition name="slide-fade">
                    <ul v-if="showProjects" class="mobile-projects">
                      <li v-for="p in projects" :key="p.id">{{p.title}}</li>
                    </ul>
                  </Transition>
                </li>
                <li><RouterLink to="/events" @click="menuOpen = false">События</RouterLink></li>
                <li><RouterLink to="/news" @click="menuOpen = false">Новости</RouterLink></li>
                <li><RouterLink to="/ukno" @click="menuOpen = false">О нас</RouterLink></li>
              </ul>
            </div>
          </div>
        </Transition>
      </Teleport>
    </nav>
  </div>
</template>


<script setup>
import { ref, computed, watch, onUnmounted, onMounted } from 'vue';
import { useDataStore } from '@/stores/counter';

const store = useDataStore();
const menuOpen = ref(false)
const showProjects = ref(false);
const projects = computed(() => store.getProject)

watch(menuOpen, (open) => {
  if (open) {
    document.body.style.position = 'fixed';
    document.body.style.top = `-${window.scrollY}px`;
    document.body.style.width = '100%';
  } else {
    const scrollY = Math.abs(parseInt(document.body.style.top || '0'));
    document.body.style.position = '';
    document.body.style.top = '';
    document.body.style.width = '';
    window.scrollTo(0, scrollY);
  }
});

onMounted(async () => {
  await store.FetchProject();
});


onUnmounted(() => {
  document.body.style.position = '';
  document.body.style.top = '';
  document.body.style.width = '';
});

const toggleProjects = () => {
  showProjects.value = !showProjects.value;
};

const hasToken = computed(() => {
  return !store.auth_key;
});

const role = computed(() => {
  return store.role;
});

const profileData = computed(() => store.getProfileData)
</script>

<style scoped>

.header-wrapper{
  width: calc(100vw - 90px);
  position: fixed;
  padding: 28px 45px;
  backdrop-filter: blur(28.399999618530273px);
  background: rgba(255, 255, 255, 0.7);
  z-index: 900;
}

.nav-list{
  width: 80%;
  margin: 0 auto;
  justify-content: space-around;
  align-items: center;
}

.profile{
  position: absolute;
  right: 45px;
  top: 50%;
  transform: translateY(-50%);
}

button{
  display: flex;
  align-items: center;
  width: 48px;
  height: 48px;
  justify-content: center;
  background-color: #FFD4C4;
  border-radius: 300px;
  color: #FF8C5B;
}


.project{
  position: relative;
  display: flex;
  align-items: center;
}

h4{
  font-family: 'Manrope';
}

.project-list{
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0px;
  left: 0;
  transform: translateX(-25%);
  top: 70px;
  background-color: white;
  box-shadow: 0 4px 10px 0 rgba(0, 0, 0, 0.04);
  border-radius: 8px;
  opacity: 0;
  visibility: hidden;
  transition: all 0.5s ease;
}

.project:hover > .project-list{
  visibility: visible;
  opacity: 1;
}

.project:hover{
  height: 70px;
}

.project-list > li{
  padding: 6px 12px;
  width: 260px;
  transition: all 0.3s ease;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
}

.project-list > li:hover{
  background-color: #EBEBEB;
}

/* Анимации для мобильного меню */
.menu-fade-enter-active,
.menu-fade-leave-active {
  transition: all 0.3s ease;
  transform-origin: top;
}

.menu-fade-enter-from,
.menu-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px) scaleY(0.95);
}

.menu-fade-enter-to,
.menu-fade-leave-from {
  opacity: 1;
  transform: translateY(0) scaleY(1);
}

/* Анимация для подменю проектов */
.slide-fade-enter-active {
  transition: all 0.3s ease;
}

.slide-fade-leave-active {
  transition: all 0.2s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-5px);
}

.slide-fade-enter-to,
.slide-fade-leave-from {
  opacity: 1;
  transform: translateY(0);
}

/* Мобильные стили */

@media (max-width: 768px) {
  .header-wrapper{
    width: calc(100vw - 48px);
    position: relative;
    padding: 56px 24px 20px 24px;
  }
}

.mobile-header{
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}

.mobile-logo {
  height: 100%;
}

.mobile-profile{
  width: 31px;
  height: 31px;
}

.mobile-profile span{
  font-size: 20px;
  font-family: 'Manrope';
  font-weight: 600;
}

.mobile-nav * button{
  width: 31px;
  height: 31px;
}

.mobile-nav button img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  box-sizing: border-box;
}

.menu-btn{
  background: none;
}

.mobile-overlay {
  position: fixed;
  inset: 0;
  z-index: 998;
}


.mobile-menu{
  display: flex;
  justify-content: center;
  position: absolute;
  width: 100%;
  top: 112px;
  left: 0;
  background-color: white;
  /* box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); */
  z-index: 999;
}

.mobile-menu > ul{
  width: calc(100% - 48px);
  border-top: 1px solid #FFECE0;
  flex-direction: column;
  padding-top: 40px;
  padding-bottom: 20px;
  gap: 18px;
}

.mobile-projects {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-left: 15px;
  padding-top: 15px;
  padding-bottom: 10px;
}

.mobile-logo > .router-main {
  display: block;
  height: 100%;
}
</style>
