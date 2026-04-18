<script setup lang="ts">
import { computed, ref } from 'vue'
import { useHead } from '@unhead/vue'
import { RouterLink } from 'vue-router'
import products from '../generated/products.json'
import type { ProductSummary } from '../types/product'

const list = products as unknown as ProductSummary[]

const query = ref('')
const stateFilter = ref<string>('')
const sortBy = ref<'name' | 'par' | 'yardage'>('name')

const states = computed(() => {
  const s = new Set<string>()
  for (const p of list) if (p.state) s.add(p.state)
  return Array.from(s).sort()
})

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  let rows = list
  if (stateFilter.value) rows = rows.filter(p => p.state === stateFilter.value)
  if (q) {
    rows = rows.filter(p =>
      (p.name || '').toLowerCase().includes(q)
      || (p.club_name || '').toLowerCase().includes(q)
      || (p.city || '').toLowerCase().includes(q),
    )
  }
  const sorted = [...rows]
  if (sortBy.value === 'par') sorted.sort((a, b) => (a.par ?? 0) - (b.par ?? 0))
  else if (sortBy.value === 'yardage') sorted.sort((a, b) => (b.yardage ?? 0) - (a.yardage ?? 0))
  else sorted.sort((a, b) => a.name.localeCompare(b.name))
  return sorted
})

const collectionLd = computed(() => ({
  '@context': 'https://schema.org',
  '@type': 'CollectionPage',
  name: 'Split the Tee — Course Glass Collection',
  url: 'https://www.splitthetee.com/products',
  hasPart: filtered.value.slice(0, 24).map(p => ({
    '@type': 'Product',
    name: `${p.name} Pint Glass`,
    url: `https://www.splitthetee.com/products/${p.slug}`,
    image: p.hero_image ? `https://www.splitthetee.com${p.hero_image}` : undefined,
  })),
}))

const collectionLdHtml = computed(
  () => `<script type="application/ld+json">${JSON.stringify(collectionLd.value)}<\/script>`,
)

useHead({
  title: 'All courses — Split the Tee',
  meta: [
    {
      name: 'description',
      content: 'Browse every pint glass etched with a real golf course. Filter by state, search by name, preorder yours today.',
    },
    { property: 'og:title', content: 'All courses — Split the Tee' },
    { property: 'og:type', content: 'website' },
    { property: 'og:url', content: 'https://www.splitthetee.com/products' },
    {
      property: 'og:description',
      content: 'Browse every pint glass etched with a real golf course.',
    },
  ],
  link: [{ rel: 'canonical', href: 'https://www.splitthetee.com/products' }],
})
</script>

<template>
  <div class="min-h-screen bg-white text-emerald-950">
    <div v-html="collectionLdHtml" class="hidden" />
    <header class="border-b border-emerald-100">
      <div class="max-w-6xl mx-auto px-6 py-5 flex items-center justify-between">
        <RouterLink to="/" class="flex items-center gap-3">
          <img
            src="/splitthetee.svg"
            alt="Split the Tee"
            class="h-8 w-auto"
          />
        </RouterLink>
        <nav class="text-sm text-emerald-700">
          <RouterLink to="/products" class="font-semibold">All courses</RouterLink>
        </nav>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-6 py-10">
      <div class="mb-8">
        <h1 class="text-3xl sm:text-4xl font-bold mb-2">Every course, on a glass.</h1>
        <p class="text-emerald-800 text-sm max-w-xl">
          Each pint glass is etched with nine holes of a real golf course. Find yours below, or
          preorder any course not yet listed.
        </p>
      </div>

      <div class="flex flex-col sm:flex-row gap-3 mb-8">
        <input
          v-model="query"
          type="search"
          placeholder="Search courses"
          class="flex-1 px-4 py-2.5 rounded-xl border border-emerald-200 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
        />
        <select
          v-model="stateFilter"
          class="px-4 py-2.5 rounded-xl border border-emerald-200 bg-white"
        >
          <option value="">All states</option>
          <option v-for="s in states" :key="s" :value="s">{{ s }}</option>
        </select>
        <select
          v-model="sortBy"
          class="px-4 py-2.5 rounded-xl border border-emerald-200 bg-white"
        >
          <option value="name">Sort: Name</option>
          <option value="par">Sort: Par</option>
          <option value="yardage">Sort: Longest</option>
        </select>
      </div>

      <p v-if="list.length === 0" class="text-emerald-700 text-sm py-20 text-center">
        Our course catalog is being built. Preorders are open — enter your course on the
        home page and we'll make yours next.
      </p>

      <p v-else-if="filtered.length === 0" class="text-emerald-700 text-sm py-20 text-center">
        No courses match your filters.
      </p>

      <div
        v-else
        class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        <RouterLink
          v-for="p in filtered"
          :key="p.slug"
          :to="`/products/${p.slug}`"
          class="group block bg-white border border-emerald-100 rounded-2xl overflow-hidden hover:shadow-xl transition-shadow"
        >
          <div class="aspect-square bg-emerald-50 flex items-center justify-center overflow-hidden">
            <img
              v-if="p.hero_image"
              :src="p.hero_image"
              :alt="`${p.name} pint glass`"
              loading="lazy"
              class="w-full h-full object-contain group-hover:scale-105 transition-transform"
            />
            <span v-else class="text-emerald-300 text-sm">Preview coming</span>
          </div>
          <div class="p-4">
            <h3 class="font-semibold text-base truncate">{{ p.name }}</h3>
            <p class="text-emerald-700 text-xs mt-0.5 truncate">
              {{ [p.city, p.state].filter(Boolean).join(', ') || p.country || '—' }}
            </p>
            <div class="flex items-center justify-between mt-3 text-xs text-emerald-600">
              <span v-if="p.par">Par {{ p.par }}</span>
              <span v-if="p.yardage">{{ p.yardage.toLocaleString() }} yd</span>
              <span class="text-emerald-900 font-semibold group-hover:underline">Preorder →</span>
            </div>
          </div>
        </RouterLink>
      </div>
    </main>
  </div>
</template>
