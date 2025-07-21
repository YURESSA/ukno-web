<template>
  <div :class="['div-wrapper', className]">
    <nav class="nav-items">
      <RouterLink :to="{ path: '/', hash: '#news' }" replace class="intro-text">О нас</RouterLink>
      <RouterLink to="/events" class="intro-text">События</RouterLink>

      <RouterLink to="/" class="logo">
        <img src="/logo/logo.svg" alt="Логотип" />
      </RouterLink>

      <RouterLink :to="{ path: '/', hash: '#news' }" replace class="intro-text">Новости</RouterLink>
      <RouterLink :to="{ path: '/', hash: '#contact' }" replace class="intro-text"
        >Контакты
      </RouterLink>

      <RouterLink
        :to="isAuthenticated ? (role === 'resident' ? '/resident-profile' : '/profile') : '/login'"
        class="profile-link"
      >
        <img src="/icon/header/iconamoon_profile-fill.svg" alt="Профиль" class="profile-icon" />
      </RouterLink>
    </nav>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useDataStore } from '@/stores/counter'

const store = useDataStore()

const isAuthenticated = computed(() => !!store.auth_key)
const role = computed(() => store.role)
</script>

<style>
.div-wrapper {
  -webkit-backdrop-filter: blur(14.2px) brightness(100%);
  backdrop-filter: blur(14.2px) brightness(100%);
  background-color: #ffffffb2;
  height: 137px;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding-bottom: 40px;
}

.nav-items {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 90%;
  max-width: 1280px;
  gap: 30px;
}

.intro-text {
  color: #333333;
  font-family: 'Manrope-Medium', Helvetica, sans-serif;
  font-size: 20px;
  font-weight: 500;
  line-height: 28px;
  text-decoration: none;
  white-space: nowrap;
}

.logo img {
  height: 81px;
}

.profile-link {
  display: flex;
  align-items: center;
}

.profile-icon {
  height: 40px;
  width: 40px;
  cursor: pointer;
}
</style>
