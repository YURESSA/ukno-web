import { createRouter, createWebHistory } from 'vue-router'
import { useDataStore } from '@/stores/counter'
import Main from '@/pages/main/main.vue'

import MainLayout from '@/layouts/MainLayout.vue'
import LoginLayout from '@/layouts/LoginLayout.vue'

import EventsFeed from '@/pages/eventFeed/eventsFeed.vue'
import EventPage from '@/pages/eventPage/eventPage.vue'
import Login from '@/pages/auth/login/login.vue'
import Registration from '@/pages/auth/registration/registration.vue'
import Payment from '@/pages/payment/payment.vue'
import UserProfile from '@/pages/personal-accounts/user/user.vue'
import ResidentProfile from '@/pages/personal-accounts/resident/resident.vue'
import AdminProfile from '@/pages/personal-accounts/admin/admin.vue'
import PanelLayout from '@/layouts/PanelLayout.vue'
import NewEvent from '@/pages/personal-accounts/_shared/newEvent.vue'
import changeEvent from '@/pages/personal-accounts/_shared/changeEvent.vue'
import News from '@/pages/news/news.vue'
import Requesits from '@/pages/requesits/requesits.vue'
import Ukno from '@/pages/ukno/ukno.vue'
import NotFoundPage from '@/components/shared/NotFoundPage.vue'
import Test from '@/pages/test.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/test-page',
      name: 'Test',
      component: Test,
    },
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
          path: '/news',
          name: 'NewsPage',
          component: News,
        },
        {
          path: '/requesits',
          name: 'requesits',
          component: Requesits,
        },
        {
          path: '/ukno',
          name: 'ukno',
          component: Ukno,
        },
      ],
    },
    {
      path: '/',
      name: 'LoginLayout',
      component: LoginLayout,
      children: [
        {
          path: '/login',
          name: 'LoginPage',
          component: Login,
        },
        {
          path: '/register',
          name: 'RegisterPage',
          component: Registration,
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
      path: '/admin-profile',
      name: 'AdminProfile',
      component: AdminProfile,
      meta: { requiresAuth: true, requiredRole: 'admin' },
    },
    {
      path: '/panel',
      component: PanelLayout,
      meta: { requiresAuth: true, requiredRole: 'admin' },
      children: [
        {
          path: '',
          redirect: { name: 'AdminUsers' }
        },
        {
          path: 'users',
          name: 'AdminUsers',
          component: () => import('@/pages/adminPanel/sections/UsersSection.vue'),
          meta: { title: 'Пользователи' }
        },
        {
          path: 'categories',
          name: 'AdminCategories',
          component: () => import('@/pages/adminPanel/sections/CategoriesSection.vue'),
          meta: { title: 'Категории' }
        },
        {
          path: 'formats',
          name: 'AdminFormats',
          component: () => import('@/pages/adminPanel/sections/FormatsSection.vue'),
          meta: { title: 'Типы форматов' }
        },
        {
          path: 'age-categories',
          name: 'AdminAge',
          component: () => import('@/pages/adminPanel/sections/AgeSection.vue'),
          meta: { title: 'Возрастные категории' }
        },
        {
          path: 'events',
          name: 'AdminEvents',
          component: () => import('@/pages/adminPanel/sections/EventsSection.vue'),
          meta: { title: 'События' }
        },
        {
          path: 'news',
          name: 'AdminNews',
          component: () => import('@/pages/adminPanel/sections/NewsSection.vue'),
          meta: { title: 'Новости' }
        },
        {
          path: 'reservations',
          name: 'AdminReservations',
          component: () => import('@/pages/adminPanel/sections/ReservationsSection.vue'),
          meta: { title: 'Брони' }
        },
        {
          path: 'team',
          name: 'AdminTeam',
          component: () => import('@/pages/adminPanel/sections/TeamSection.vue'),
          meta: { title: 'Команда' }
        },
        {
          path: 'cultural-space',
          name: 'CulturalSpace',
          component: () => import('@/pages/adminPanel/sections/CulturalSpace.vue'),
          meta: { title: 'Культурное пространство' }
        },
      ]
    },
    {
      path: '/newEvent',
      name: 'NewEvent',
      component: NewEvent,
      meta: { requiresAuth: true, requiredRole: 'resident' },
    },
    {
      path: '/change-event/:id',
      name: 'changeEvent',
      component: changeEvent,
      meta: { requiresAuth: true, requiredRole: 'resident' },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: NotFoundPage
    }
  ],
    scrollBehavior() {
    return { top: 0 }
  }
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
