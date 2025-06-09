import { createRouter, createWebHistory } from 'vue-router'
import Main from '@/pages/main/main.vue'
import Filter from '@/pages/eventFeed/components/filter.vue'
import MainLayout from '@/layouts/MainLayout.vue'
import EventsFeed from '@/pages/eventFeed/eventsFeed.vue'
import EventPage from '@/pages/eventPage/eventPage.vue'
import Login from '@/pages/auth/login/login.vue'
import Registration from '@/pages/auth/registration/registration.vue'
import Payment from '@/pages/payment/payment.vue'
import UserProfile from '@/pages/personal-accounts/user/user.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Main',
      component: MainLayout,
      children: [
        {
          path: '/',
          name: 'MainPage',
          component: Main,
        },
        {
          path: '/events',
          name: 'EventsPage',
          component: EventsFeed,
        },
        {
          path: '/events/:id',
          name: 'EventDetailPage',
          component: EventPage,
        },
        {
          path: '/login',
          name: 'LoginPage',
          component: Login,
        },
        {
          path: '/register',
          name: 'registerPage',
          component: Registration,
        },
      ],
    },
    {
      path: '/payment/:id',
      name: 'Payment',
      component: Payment,
    },
    {
      path: '/profile',
      name: 'Profile',
      component: UserProfile,
    },
    // {
    //   //временный
    //   path: '/filter',
    //   name: 'Filter',
    //   component: Filter,
    // },
  ],
})

export default router
