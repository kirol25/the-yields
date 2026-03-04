<template>
  <div class="relative" :style="{ width: `${size}px`, height: `${size}px` }">
    <Doughnut :data="chartData" :options="chartOptions" />
    <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
      <span
        class="text-xl font-bold tabular-nums"
        :class="exceeded ? 'text-amber-400' : 'text-white'"
      >{{ displayPct }}%</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip } from 'chart.js'

ChartJS.register(ArcElement, Tooltip)

const props = defineProps({
  achieved:        { type: Number, required: true },
  goal:            { type: Number, required: true },
  size:            { type: Number, default: 140 },
  counterclockwise: { type: Boolean, default: false },
  canExceed:       { type: Boolean, default: false },
})

const exceeded = computed(() => props.canExceed && props.achieved > props.goal)

// Always show the real % in the center; cap at 100 only when canExceed is false
const displayPct = computed(() =>
  props.goal > 0 ? Math.round((props.achieved / props.goal) * 100) : 0,
)

const EMERALD = ['rgba(52, 211, 153, 0.9)', 'rgba(31, 41, 55, 0.8)']
const AMBER   = ['rgba(245, 158, 11, 0.9)', 'rgba(31, 41, 55, 0.8)']
const BORDER_EMERALD = ['rgb(52, 211, 153)', 'rgb(55, 65, 81)']
const BORDER_AMBER   = ['rgb(245, 158, 11)', 'rgb(55, 65, 81)']

const chartData = computed(() => {
  const filled    = Math.min(props.achieved, props.goal)
  const remaining = Math.max(props.goal - props.achieved, 0)
  const colors    = exceeded.value || props.counterclockwise ? AMBER : EMERALD
  const borders   = exceeded.value || props.counterclockwise ? BORDER_AMBER : BORDER_EMERALD

  // Counterclockwise: put remaining first so the filled arc appears to go left from 12 o'clock
  const data = props.counterclockwise
    ? [remaining, filled]
    : [filled, remaining]
  const bg   = props.counterclockwise ? [colors[1], colors[0]] : colors
  const bc   = props.counterclockwise ? [borders[1], borders[0]] : borders

  return {
    datasets: [{ data, backgroundColor: bg, borderColor: bc, borderWidth: 1, hoverOffset: 2 }],
  }
})

const chartOptions = {
  cutout: '72%',
  responsive: true,
  maintainAspectRatio: true,
  animation: { duration: 600, easing: 'easeInOutQuart' },
  plugins: {
    legend: { display: false },
    tooltip: { enabled: false },
  },
}
</script>
