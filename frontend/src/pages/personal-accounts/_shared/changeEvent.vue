<template>
  <ResidentEventEditor :key="route.params.id" />
</template>

<script setup>
import { useRoute } from 'vue-router'
import ResidentEventEditor from './ResidentEventEditor.vue'
const route = useRoute()
</script>