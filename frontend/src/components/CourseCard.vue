<script setup lang="ts">
defineProps<{
  course: any
  selected: boolean
}>()
</script>

<template>
  <div
    class="px-4 py-3 border-b border-gray-800 cursor-pointer transition-colors"
    :class="selected ? 'bg-emerald-900/50 border-l-4 border-l-emerald-400' : 'hover:bg-gray-800'"
  >
    <h3 class="text-sm font-semibold text-white">{{ course.course_name }}</h3>
    <p v-if="course.club_name !== course.course_name" class="text-xs text-gray-500 mt-0.5">
      {{ course.club_name }}
    </p>
    <p class="text-xs text-gray-400 mt-1">{{ course.locationStr }}</p>
    <div v-if="course.stats" class="flex gap-3 mt-2 flex-wrap">
      <span class="text-xs text-gray-400">Par <strong class="text-emerald-400">{{ course.stats.par }}</strong></span>
      <span class="text-xs text-gray-400"><strong class="text-emerald-400">{{ course.stats.yards?.toLocaleString() }}</strong> yds</span>
      <span class="text-xs text-gray-400">Rating <strong class="text-emerald-400">{{ course.stats.rating }}</strong></span>
      <span class="text-xs text-gray-400">Slope <strong class="text-emerald-400">{{ course.stats.slope }}</strong></span>
    </div>
  </div>
</template>
