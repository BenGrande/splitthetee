<script setup lang="ts">
import { ref } from 'vue'
import { useGameStore } from '../stores/game'

const game = useGameStore()
const scoreFlash = ref<number | null>(null)
let touchStartX = 0

const scoreOptions = [-1, 0, 1, 2, 3, 4, 5]

function vibrate() {
  try { navigator.vibrate?.(30) } catch { /* not available */ }
}

async function handleScore(score: number) {
  const actual = game.currentHoleInfo.par + score
  const ok = await game.submitScore(game.currentHole, actual)
  if (ok !== false) {
    vibrate()
    scoreFlash.value = score
    setTimeout(() => {
      scoreFlash.value = null
      game.advanceToNextUnscored()
    }, 600)
  }
}

async function handlePenalty() {
  const actual = game.currentHoleInfo.par + 8
  await game.submitScore(game.currentHole, actual)
  vibrate()
  scoreFlash.value = 8
  setTimeout(() => {
    scoreFlash.value = null
    game.advanceToNextUnscored()
  }, 600)
}

function onTouchStart(e: TouchEvent) {
  touchStartX = e.touches[0].clientX
}

function onTouchEnd(e: TouchEvent) {
  const dx = e.changedTouches[0].clientX - touchStartX
  if (Math.abs(dx) > 60) {
    if (dx > 0) game.prevHole()
    else game.nextHole()
  }
}

function currentScoreRelPar(): number | null {
  const s = game.scores[game.currentHole]
  if (s === undefined) return null
  return s - game.currentHoleInfo.par
}

function scoreLabel(rel: number): string {
  if (rel === 0) return 'E'
  return rel > 0 ? `+${rel}` : `${rel}`
}

function formatCumulative(n: number): string {
  if (n === 0) return 'E'
  return n > 0 ? `+${n}` : `${n}`
}
</script>

<template>
  <div class="min-h-screen bg-emerald-950 text-white flex flex-col">
    <!-- Header -->
    <header class="bg-emerald-900 px-4 py-3 flex items-center justify-between shrink-0">
      <div>
        <h1 class="text-lg font-bold">One Nine</h1>
        <p class="text-emerald-400 text-xs">{{ game.courseName }}</p>
      </div>
      <div class="text-right">
        <div class="text-sm font-medium">Hole {{ game.currentHole }}/{{ game.totalHoles }}</div>
        <div class="text-xs text-emerald-400">{{ game.playerName }}</div>
      </div>
    </header>

    <!-- Main Content -->
    <main
      ref="mainEl"
      class="flex-1 flex flex-col items-center px-4 py-6 max-w-lg mx-auto w-full"
      @touchstart="onTouchStart"
      @touchend="onTouchEnd"
    >
      <!-- Hole Info Card -->
      <div class="w-full bg-emerald-900/40 rounded-2xl p-5 border border-emerald-800/50 mb-6 text-center">
        <div class="text-emerald-400/70 text-xs mb-1">Glass {{ game.currentGlassNumber }}</div>
        <div class="text-3xl font-bold mb-1">Hole {{ game.currentHole }}</div>
        <div class="text-emerald-300 text-sm">
          Par {{ game.currentHoleInfo.par }}
          <span v-if="game.currentHoleInfo.yards"> &middot; {{ game.currentHoleInfo.yards }}yd</span>
          <span v-if="game.currentHoleInfo.handicap"> &middot; HCP {{ game.currentHoleInfo.handicap }}</span>
        </div>
        <div class="mt-2 text-xs text-emerald-500">
          Running: <span class="font-semibold text-emerald-300">{{ formatCumulative(game.cumulativeScore) }}</span>
          &middot; {{ game.holesScored }} holes scored
        </div>
      </div>

      <!-- Score Buttons -->
      <div class="w-full mb-4">
        <p class="text-sm text-emerald-400/80 text-center mb-3">Your Score (relative to par)</p>
        <div class="grid grid-cols-7 gap-2">
          <button
            v-for="rel in scoreOptions"
            :key="rel"
            @click="handleScore(rel)"
            class="py-4 rounded-xl text-lg font-bold transition-all duration-150 active:scale-95"
            :class="[
              currentScoreRelPar() === rel
                ? 'bg-emerald-500 text-white ring-2 ring-emerald-300'
                : 'bg-emerald-900/60 text-emerald-200 hover:bg-emerald-800 border border-emerald-700/50',
              scoreFlash === rel ? 'bg-green-400 text-green-900 scale-110' : ''
            ]"
          >
            {{ scoreLabel(rel) }}
          </button>
        </div>
        <button
          @click="handlePenalty"
          class="w-full mt-3 py-3 rounded-xl text-sm font-semibold bg-red-900/40 text-red-300 border border-red-800/50 hover:bg-red-900/60 transition-colors active:scale-[0.98]"
          :class="[
            currentScoreRelPar() === 8 ? 'ring-2 ring-red-400 bg-red-800/50' : '',
            scoreFlash === 8 ? 'bg-red-500 text-white' : ''
          ]"
        >
          +8 Penalty
        </button>
        <button
          v-if="game.lastScoredHole"
          @click="game.undoLastScore()"
          class="w-full mt-2 py-2 rounded-xl text-xs text-gray-400 hover:text-gray-200 transition-colors"
          aria-label="Undo last score"
        >
          Undo last score
        </button>
      </div>

      <!-- Hole Navigator -->
      <div class="w-full flex items-center justify-center gap-4 mb-6">
        <button
          @click="game.prevHole()"
          :disabled="game.currentHole <= 1"
          class="w-12 h-12 rounded-full bg-emerald-900/60 border border-emerald-700/50 flex items-center justify-center text-xl disabled:opacity-30 disabled:cursor-not-allowed hover:bg-emerald-800 transition-colors"
          aria-label="Previous hole"
        >&larr;</button>
        <span class="text-lg font-semibold w-24 text-center">Hole {{ game.currentHole }}</span>
        <button
          @click="game.nextHole()"
          :disabled="game.currentHole >= game.totalHoles"
          class="w-12 h-12 rounded-full bg-emerald-900/60 border border-emerald-700/50 flex items-center justify-center text-xl disabled:opacity-30 disabled:cursor-not-allowed hover:bg-emerald-800 transition-colors"
          aria-label="Next hole"
        >&rarr;</button>
      </div>

      <!-- Leaderboard Link -->
      <button
        @click="game.view = 'leaderboard'"
        class="px-6 py-3 rounded-xl bg-emerald-900/40 border border-emerald-700/50 text-emerald-300 text-sm font-medium hover:bg-emerald-800/60 transition-colors"
      >
        View Leaderboard
      </button>
    </main>

    <!-- Progress Dots -->
    <footer class="px-4 py-3 bg-emerald-900/30 shrink-0">
      <div class="flex justify-center gap-1.5 flex-wrap max-w-lg mx-auto">
        <span
          v-for="h in game.totalHoles"
          :key="h"
          @click="game.currentHole = h"
          class="w-3 h-3 rounded-full cursor-pointer transition-all"
          :class="[
            h === game.currentHole
              ? 'bg-emerald-300 scale-125'
              : game.scores[h] !== undefined
                ? 'bg-emerald-600'
                : 'bg-emerald-900 border border-emerald-700',
          ]"
        />
      </div>
    </footer>
  </div>
</template>
