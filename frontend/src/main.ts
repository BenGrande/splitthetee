import { ViteSSG } from 'vite-ssg'
import { createPinia } from 'pinia'
import type { RouteRecordRaw } from 'vue-router'
import './style.css'
import App from './App.vue'
import { routes } from './router'
import productsManifest from './generated/products.json'

type ManifestEntry = { slug: string }
const manifest = productsManifest as ManifestEntry[]

export const createApp = ViteSSG(
  App,
  { routes, base: '/' },
  ({ app, isClient }) => {
    app.use(createPinia())

    if (isClient && 'serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').catch(() => {
          // SW registration failed — app still works without it
        })
      })
    }
  },
)

export async function includedRoutes(
  _paths: string[],
  allRoutes: readonly RouteRecordRaw[],
) {
  const staticPaths = allRoutes
    .filter((r) => {
      if (!r.path) return false
      if (r.path.includes(':')) return false
      if (r.meta?.noPrerender) return false
      if (r.path.startsWith('/render')) return false
      return true
    })
    .map((r) => r.path)

  const productPaths = manifest.map((p) => `/products/${p.slug}`)
  return Array.from(new Set([...staticPaths, ...productPaths]))
}
