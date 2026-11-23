<template>
  <s-header v-if="!hideHeaderAndFooter" />
  <div>
    <router-view />
  </div>
  <s-footer v-if="!hideHeaderAndFooter" />
</template>

<script setup>
import { provide, ref } from 'vue';
import { SHeader, SFooter } from '@shared';

const hideHeaderAndFooter = ref(false);

provide('set-main-header-and-footer-hidden', (hidden) => {
  hideHeaderAndFooter.value = hidden;
});
</script>

<style scoped>

</style>
