<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCourseStore } from '../stores/course'
import CourseCard from '../components/CourseCard.vue'

const router = useRouter()
const store = useCourseStore()
const query = ref('')

function getTeeStats(course: any) {
  const maleTees = course.tees?.male || []
  const femaleTees = course.tees?.female || []
  const allTees = [...maleTees, ...femaleTees]
  if (allTees.length === 0) return null

  const primary =
    maleTees.length > 0
      ? maleTees.reduce((a: any, b: any) => (a.total_yards > b.total_yards ? a : b))
      : allTees.reduce((a: any, b: any) => (a.total_yards > b.total_yards ? a : b))

  return {
    par: primary.par_total,
    yards: primary.total_yards,
    rating: primary.course_rating,
    slope: primary.slope_rating,
    holes: primary.number_of_holes,
  }
}

const coursesWithStats = computed(() =>
  store.courses.map((c: any) => ({
    ...c,
    stats: getTeeStats(c),
    locationStr: [
      c.location?.city,
      c.location?.state,
      c.location?.country !== 'United States' ? c.location?.country : '',
    ]
      .filter(Boolean)
      .join(', '),
  }))
)

const hasSearched = ref(false)

async function doSearch() {
  if (!query.value.trim()) return
  hasSearched.value = true
  await store.search(query.value)
}

function selectCourse(course: any) {
  store.loadCourse(course)
}

function openDesigner() {
  if (!store.selectedCourse) return
  const c = store.selectedCourse
  router.push({
    name: 'designer',
    query: {
      lat: c.location.latitude,
      lng: c.location.longitude,
      courseId: c.id,
    },
  })
}
</script>

<template>
  <div class="flex flex-col h-screen">
    <!-- Header -->
    <header class="bg-emerald-900 text-white px-6 py-4 flex items-center gap-4 shrink-0">
      <img src="/logo.png" alt="One Nine" class="w-8 h-8 rounded" />
      <h1 class="text-xl font-semibold tracking-tight">One Nine</h1>
      <form class="flex-1 max-w-md flex gap-2" @submit.prevent="doSearch">
        <input
          v-model="query"
          type="text"
          placeholder="Search golf courses..."
          aria-label="Search golf courses"
          class="flex-1 px-3 py-2 rounded text-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
          autofocus
        />
        <button
          type="submit"
          :disabled="store.loading"
          class="px-4 py-2 bg-emerald-700 hover:bg-emerald-600 disabled:opacity-60 disabled:cursor-not-allowed rounded text-sm font-medium transition-colors"
        >
          <span v-if="store.loading" class="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          <span v-else>Search</span>
        </button>
      </form>
    </header>

    <!-- Two-panel layout -->
    <div class="flex flex-1 min-h-0 flex-col md:flex-row">
      <!-- Left sidebar -->
      <aside class="w-full md:w-[380px] md:min-w-[380px] bg-gray-900 text-white overflow-y-auto border-r border-gray-700">
        <!-- Results header -->
        <div class="px-4 py-3 text-sm text-gray-400 border-b border-gray-700 bg-gray-900/80">
          <span v-if="store.loading">Searching...</span>
          <span v-else-if="!hasSearched">Search for a golf course to get started</span>
          <span v-else-if="store.courses.length === 0">No courses found</span>
          <span v-else>{{ store.courses.length }} course{{ store.courses.length !== 1 ? 's' : '' }} found</span>
        </div>

        <!-- Results list -->
        <div v-if="!hasSearched && !store.loading" class="p-8 text-center text-gray-500 text-sm">
          Enter a course name, city, or state to find golf courses.
        </div>
        <div v-else-if="hasSearched && store.courses.length === 0 && !store.loading" class="p-8 text-center text-gray-500 text-sm">
          Try a different search term.
        </div>
        <div v-else>
          <CourseCard
            v-for="course in coursesWithStats"
            :key="course.id"
            :course="course"
            :selected="store.selectedCourse?.id === course.id"
            @click="selectCourse(course)"
          />
        </div>
      </aside>

      <!-- Right main area -->
      <main class="flex-1 bg-gray-50 overflow-y-auto">
        <!-- Empty state -->
        <div v-if="!store.selectedCourse" class="flex items-center justify-center h-full text-gray-400 text-center p-8">
          <div>
            <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <p class="text-lg font-medium">Select a course</p>
            <p class="text-sm mt-1">Search and click a course to view details</p>
          </div>
        </div>

        <!-- Course detail -->
        <div v-else class="p-6 md:p-8 max-w-3xl">
          <!-- Loading hole data -->
          <div v-if="store.loading" class="flex items-center gap-3 text-gray-500">
            <span class="inline-block w-5 h-5 border-2 border-gray-300 border-t-emerald-600 rounded-full animate-spin" />
            Loading course details...
          </div>

          <template v-else>
            <!-- Course header -->
            <div class="mb-6">
              <h2 class="text-2xl font-bold text-gray-900">{{ store.selectedCourse.course_name }}</h2>
              <p v-if="store.selectedCourse.club_name !== store.selectedCourse.course_name" class="text-sm text-gray-500 mt-1">
                {{ store.selectedCourse.club_name }}
              </p>
              <p class="text-sm text-gray-600 mt-1">
                {{ [store.selectedCourse.location?.city, store.selectedCourse.location?.state].filter(Boolean).join(', ') }}
              </p>

              <!-- Stats bar -->
              <div v-if="coursesWithStats.find((c: any) => c.id === store.selectedCourse.id)?.stats" class="flex gap-4 mt-4 flex-wrap">
                <div
                  v-for="(item, idx) in [
                    { label: 'Par', value: coursesWithStats.find((c: any) => c.id === store.selectedCourse.id)?.stats?.par },
                    { label: 'Yards', value: coursesWithStats.find((c: any) => c.id === store.selectedCourse.id)?.stats?.yards?.toLocaleString() },
                    { label: 'Rating', value: coursesWithStats.find((c: any) => c.id === store.selectedCourse.id)?.stats?.rating },
                    { label: 'Slope', value: coursesWithStats.find((c: any) => c.id === store.selectedCourse.id)?.stats?.slope },
                  ]"
                  :key="idx"
                  class="bg-white rounded-lg px-4 py-2 shadow-sm border border-gray-200"
                >
                  <div class="text-xs text-gray-500 uppercase tracking-wide">{{ item.label }}</div>
                  <div class="text-lg font-semibold text-emerald-800">{{ item.value }}</div>
                </div>
              </div>
            </div>

            <!-- Hole table -->
            <div v-if="store.courseData?.holes?.length" class="mb-6">
              <h3 class="text-lg font-semibold text-gray-800 mb-3">Hole Details</h3>
              <div class="overflow-x-auto rounded-lg border border-gray-200">
                <table class="w-full text-sm">
                  <thead class="bg-gray-100">
                    <tr>
                      <th class="px-3 py-2 text-left font-medium text-gray-600">Hole</th>
                      <th class="px-3 py-2 text-center font-medium text-gray-600">Par</th>
                      <th class="px-3 py-2 text-center font-medium text-gray-600">Yards</th>
                      <th class="px-3 py-2 text-center font-medium text-gray-600">Handicap</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="hole in store.courseData.holes"
                      :key="hole.number"
                      class="border-t border-gray-100 hover:bg-gray-50"
                    >
                      <td class="px-3 py-2 font-medium text-gray-900">{{ hole.number }}</td>
                      <td class="px-3 py-2 text-center text-gray-700">{{ hole.par }}</td>
                      <td class="px-3 py-2 text-center text-gray-700">{{ hole.yards }}</td>
                      <td class="px-3 py-2 text-center text-gray-700">{{ hole.handicap }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Actions -->
            <button
              @click="openDesigner"
              class="px-6 py-3 bg-emerald-800 hover:bg-emerald-700 text-white rounded-lg font-medium transition-colors shadow-sm"
            >
              Open Designer
            </button>
          </template>
        </div>
      </main>
    </div>
  </div>
</template>
