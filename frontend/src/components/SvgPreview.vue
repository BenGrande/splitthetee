<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

defineProps<{
  svgContent: string
  loading: boolean
}>()

const emit = defineEmits<{
  resetZoom: []
}>()

const container = ref<HTMLElement | null>(null)

const zoom = ref(1)
const panX = ref(0)
const panY = ref(0)
let isPanning = false
let startMX = 0
let startMY = 0
let startPX = 0
let startPY = 0

function onWheel(e: WheelEvent) {
  e.preventDefault()
  const factor = e.deltaY > 0 ? 0.9 : 1.1
  const rect = container.value!.getBoundingClientRect()
  const mx = e.clientX - rect.left - rect.width / 2
  const my = e.clientY - rect.top - rect.height / 2
  panX.value = mx - (mx - panX.value) * factor
  panY.value = my - (my - panY.value) * factor
  zoom.value *= factor
}

function onMouseDown(e: MouseEvent) {
  if (e.button !== 0) return
  isPanning = true
  startMX = e.clientX
  startMY = e.clientY
  startPX = panX.value
  startPY = panY.value
}

function onMouseMove(e: MouseEvent) {
  if (!isPanning) return
  panX.value = startPX + (e.clientX - startMX)
  panY.value = startPY + (e.clientY - startMY)
}

function onMouseUp() {
  isPanning = false
}

function resetZoom() {
  zoom.value = 1
  panX.value = 0
  panY.value = 0
}

defineExpose({ resetZoom })

onMounted(() => {
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
})
</script>

<template>
  <div
    ref="container"
    class="flex-1 overflow-hidden cursor-grab active:cursor-grabbing flex items-center justify-center bg-[#111] relative"
    @wheel.prevent="onWheel"
    @mousedown="onMouseDown"
  >
    <!-- Loading overlay -->
    <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-black/40 z-10">
      <div class="flex items-center gap-3 text-gray-400">
        <span class="inline-block w-5 h-5 border-2 border-gray-600 border-t-emerald-400 rounded-full animate-spin" />
        Rendering...
      </div>
    </div>

    <!-- SVG content -->
    <div
      ref="inner"
      class="origin-center"
      :style="{ transform: `translate(${panX}px, ${panY}px) scale(${zoom})` }"
    >
      <div v-if="!svgContent" class="text-gray-600 text-sm p-10 text-center">
        Search and select a course to begin
      </div>
      <div v-else v-html="svgContent" class="[&>svg]:block [&>svg]:max-w-[95vw] [&>svg]:max-h-[calc(100vh-140px)]" />
    </div>
  </div>
</template>
