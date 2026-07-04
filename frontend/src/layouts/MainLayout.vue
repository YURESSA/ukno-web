<template>
  <s-header />
  <div>
    <router-view />
  </div>
  <s-footer />
</template>

<script setup>
import { SHeader, SFooter } from '@shared';
</script>

<style scoped>

</style>
