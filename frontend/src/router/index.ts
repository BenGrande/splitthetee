import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'search',
      component: () => import('../views/SearchView.vue'),
    },
    {
      path: '/designer',
      name: 'designer',
      component: () => import('../views/DesignerView.vue'),
    },
    {
      path: '/play/:glassSetId',
      name: 'play',
      component: () => import('../views/PlayView.vue'),
    },
  ],
})

export default router
