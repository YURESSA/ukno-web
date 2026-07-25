<script setup>
import { RouterView } from 'vue-router'
import { useNotification } from '@/composables/useNotification'
import Alert from '@/components/ui/alert.vue'
import { NConfigProvider, ruRU, dateRuRU } from 'naive-ui'

const themeOverrides = {
  common: {
    primaryColor: '#F25C03',
    primaryColorHover: '#FF7F3F',
    primaryColorPressed: '#D95202',
    primaryColorSuppl: '#FF7F3F'
  }
}

const {
  showNotification,
  notificationMessage,
  notificationType,
  closeNotification
} = useNotification()
</script>

<template>
  <n-config-provider :locale="ruRU" :date-locale="dateRuRU" :theme-overrides="themeOverrides">
    <router-view />
    <alert
      :show="showNotification"
      :message="notificationMessage"
      :type="notificationType"
      @close="closeNotification"
    />
  </n-config-provider>
</template>

<style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}
</style>
