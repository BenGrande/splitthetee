<script setup lang="ts">
import { useDesignerStore, ALL_LAYERS, LAYER_LABELS } from '../stores/designer'

const store = useDesignerStore()

function colorToHex(c: string): string {
  if (!c || c === 'none') return '#000000'
  if (c.startsWith('#') && c.length >= 7) return c.slice(0, 7)
  if (c.startsWith('#')) return c + '000000'.slice(c.length - 1)
  if (c.startsWith('rgb')) {
    const m = c.match(/[\d.]+/g)
    if (m) {
      return `#${parseInt(m[0]).toString(16).padStart(2, '0')}${parseInt(m[1]).toString(16).padStart(2, '0')}${parseInt(m[2]).toString(16).padStart(2, '0')}`
    }
  }
  return '#000000'
}

function getSwatchColor(layer: string): string {
  const s = store.styles[layer]
  if (!s) return '#888'
  const fill = s.fill && s.fill !== 'none' ? s.fill : s.stroke || '#888'
  return colorToHex(fill)
}
</script>

<template>
  <div>
    <!-- Layer Toggles -->
    <div class="mb-4">
      <h3 class="text-[10px] uppercase tracking-wider text-gray-500 mb-2">Layers</h3>
      <div class="space-y-1">
        <label
          v-for="layer in ALL_LAYERS"
          :key="layer"
          class="flex items-center gap-2 text-xs text-gray-400 cursor-pointer hover:text-gray-300"
        >
          <input
            type="checkbox"
            :checked="!store.hiddenLayers.has(layer)"
            @change="store.toggleLayer(layer)"
            class="accent-emerald-500 w-3.5 h-3.5"
          />
          <span
            class="w-2.5 h-2.5 rounded-sm border border-white/15 shrink-0"
            :style="{ background: getSwatchColor(layer) }"
          />
          {{ LAYER_LABELS[layer] || layer }}
        </label>
      </div>
    </div>

    <!-- Style Editor -->
    <div>
      <h3 class="text-[10px] uppercase tracking-wider text-gray-500 mb-2">Styles</h3>
      <div class="space-y-1.5">
        <div
          v-for="layer in ALL_LAYERS"
          :key="layer"
          v-show="!store.hiddenLayers.has(layer)"
          class="flex items-center gap-1.5"
        >
          <span class="text-[10px] text-gray-500 w-14 shrink-0 truncate">{{ LAYER_LABELS[layer] || layer }}</span>
          <input
            type="color"
            :value="colorToHex(store.styles[layer]?.fill || '#000')"
            @input="store.updateStyle(layer, 'fill', ($event.target as HTMLInputElement).value)"
            title="Fill color"
            class="w-6 h-5 p-0.5 bg-gray-800 border border-gray-700 rounded cursor-pointer"
          />
          <input
            type="color"
            :value="colorToHex(store.styles[layer]?.stroke || '#000')"
            @input="store.updateStyle(layer, 'stroke', ($event.target as HTMLInputElement).value)"
            title="Stroke color"
            class="w-6 h-5 p-0.5 bg-gray-800 border border-gray-700 rounded cursor-pointer"
          />
          <input
            type="number"
            :value="store.styles[layer]?.strokeWidth || 0"
            @input="store.updateStyle(layer, 'strokeWidth', parseFloat(($event.target as HTMLInputElement).value) || 0)"
            min="0"
            max="5"
            step="0.1"
            title="Stroke width"
            class="w-10 px-1 py-0.5 text-[10px] bg-gray-800 border border-gray-700 rounded text-gray-300 focus:outline-none focus:border-emerald-600"
          />
        </div>
      </div>
    </div>
  </div>
</template>
