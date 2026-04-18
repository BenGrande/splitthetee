import type { RouteRecordRaw } from 'vue-router'

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'landing',
    component: () => import('../views/LandingView.vue'),
  },
  {
    path: '/products',
    name: 'products-index',
    component: () => import('../views/ProductsIndexView.vue'),
  },
  {
    path: '/products/:slug',
    name: 'product',
    component: () => import('../views/ProductView.vue'),
    props: true,
  },
  {
    path: '/render/glass/:slug',
    name: 'render-glass',
    component: () => import('../views/RenderGlassView.vue'),
    meta: { noPrerender: true, noindex: true },
    props: true,
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
]
