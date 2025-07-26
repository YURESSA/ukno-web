import { createRouter, createWebHistory } from 'vue-router'
import { useDataStore } from '@/stores/counter'
import Main from '@/pages/main/main.vue'
import MainLayout from '@/layouts/MainLayout.vue'
import EventsFeed from '@/pages/eventFeed/eventsFeed.vue'
import EventPage from '@/pages/eventPage/eventPage.vue'
import Login from '@/pages/auth/login/login.vue'
import AdminLogin from '@/pages/auth/admin/adminLogin.vue'
import ResidentLogin from '@/pages/auth/resident/residentLogin.vue'
import Registration from '@/pages/auth/registration/registration.vue'
import Payment from '@/pages/payment/payment.vue'
import UserProfile from '@/pages/personal-accounts/user/user.vue'
import ResidentProfile from '@/pages/personal-accounts/resident/resident.vue'
import NewEvent from '@/pages/personal-accounts/_shared/newEvent.vue'
import News from '@/pages/news/news.vue'

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
          path: '/resident-login',
          name: 'ResidentLogin',
          component: ResidentLogin,
        },
        {
          path: '/admin-login',
          name: 'AdminLogin',
          component: AdminLogin,
        },
        {
          path: '/register',
          name: 'RegisterPage',
          component: Registration,
        },
        {
          path: '/news',
          name: 'NewsPage',
          component: News,
        },
      ],
    },
    {
      path: '/payment/:id',
      name: 'Payment',
      component: Payment,
      meta: { requiresAuth: true },
    },
    {
      path: '/profile',
      name: 'Profile',
      component: UserProfile,
      meta: { requiresAuth: true, requiredRole: 'user' },
    },
    {
      path: '/resident-profile',
      name: 'ResidentProfile',
      component: ResidentProfile,
      meta: { requiresAuth: true, requiredRole: 'resident' },
    },
    {
      path: '/newEvent',
      name: 'NewEvent',
      component: NewEvent,
      meta: { requiresAuth: true, requiredRole: 'resident' },
    },
  ],
})

router.beforeEach((to, from, next) => {
  const store = useDataStore()

  if (to.meta.requiresAuth) {
    if (!store.auth_key) {
      return next('/login')
    }

    if (to.meta.requiredRole && store.role !== to.meta.requiredRole) {
      return next('/')
    }
  }

  next()
})

export default router
