import { createRouter, createWebHistory } from 'vue-router'
import Main from '@/page/main.vue'
import Filter from '@/components/filters/filter.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Main,
    },
    {
      //временный
      path: '/filter',
      name: 'Filter',
      component: Filter,
    },
  ],
})

export default router
