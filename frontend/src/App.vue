<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { useNotification } from '@/composables/useNotification'
import { useAdminAccessMonitor } from '@/composables/useAdminAccessMonitor'
import Alert from '@/components/ui/alert.vue'
import BaseButton from '@/components/ui/button/BaseButton.vue'
import LoadingAnimation from '@/components/shared/loading-animation.vue'
import { NConfigProvider, ruRU, dateRuRU } from 'naive-ui'

const { canRenderRoute, accessUnavailable, isChecking, refreshAdminAccess } = useAdminAccessMonitor()

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
    <router-view v-if="canRenderRoute" />
    <alert
      :show="showNotification"
      :message="notificationMessage"
      :type="notificationType"
      @close="closeNotification"
    />
  </n-config-provider>
  <Teleport to="body">
    <div class="admin-access-loader">
      <div v-if="accessUnavailable && !isChecking" class="admin-access-error">
        <p role="alert">Не удалось проверить доступ. Попробуйте ещё раз.</p>
        <BaseButton text="Повторить" @click="refreshAdminAccess" />
        <RouterLink to="/">На главную</RouterLink>
      </div>
      <div v-else role="status" aria-label="Проверяем доступ к админке">
        <LoadingAnimation />
      </div>
    </div>
  </Teleport>
</template>

<style>
.admin-access-loader {
  display: none;
  position: fixed;
  inset: 0;
}

html:is(.admin-access-pending, .admin-navigation-pending, .admin-access-unavailable) body > :not(.admin-access-loader) {
  display: none !important;
}

html:is(.admin-access-pending, .admin-navigation-pending, .admin-access-unavailable) .admin-access-loader {
  display: block;
}

.admin-access-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  min-height: 100%;
  padding: 24px;
  box-sizing: border-box;
  background: white;
  text-align: center;
}

.admin-access-error a {
  text-decoration: underline;
}
</style>

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
