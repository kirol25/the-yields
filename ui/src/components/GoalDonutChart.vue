<template>
  <div class="relative" :style="{ width: `${size}px`, height: `${size}px` }">
    <Doughnut :data="chartData" :options="chartOptions" />
    <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
      <span class="text-xl font-bold tabular-nums" :class="textClass">
        {{ noGoal ? '—' : displayPct + '%' }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip } from 'chart.js'

ChartJS.register(ArcElement, Tooltip)

const props = defineProps({
  achieved:         { type: Number, required: true },
  goal:             { type: Number, required: true },
  size:             { type: Number, default: 100 },
  counterclockwise: { type: Boolean, default: false },
  canExceed:        { type: Boolean, default: false },
  color:            { type: String, default: 'emerald' }, // 'emerald' | 'blue'
})

const noGoal   = computed(() => props.goal === 0)
const exceeded = computed(() => props.canExceed && props.achieved > props.goal)

const displayPct = computed(() =>
  props.goal > 0 ? Math.round((props.achieved / props.goal) * 100) : 0,
)

const FILL   = { emerald: 'rgba(52, 211, 153, 0.9)', blue: 'rgba(96, 165, 250, 0.9)', amber: 'rgba(245, 158, 11, 0.9)' }
const BORDER = { emerald: 'rgb(52, 211, 153)',        blue: 'rgb(96, 165, 250)',        amber: 'rgb(245, 158, 11)' }
const GRAY_FILL   = 'rgba(31, 41, 55, 0.8)'
const GRAY_BORDER = 'rgb(55, 65, 81)'

const activeColor = computed(() => (props.counterclockwise || exceeded.value) ? 'amber' : props.color)

const textClass = computed(() => {
  if (noGoal.value) return 'text-gray-600'
  if (exceeded.value) return 'text-amber-400'
  return props.counterclockwise ? 'text-amber-300' : 'text-white'
})

const chartData = computed(() => {
  if (noGoal.value) {
    return { datasets: [{ data: [1], backgroundColor: [GRAY_FILL], borderColor: [GRAY_BORDER], borderWidth: 1, hoverOffset: 0 }] }
  }

  const filled    = Math.min(props.achieved, props.goal)
  const remaining = Math.max(props.goal - props.achieved, 0)
  const fill   = FILL[activeColor.value]
  const border = BORDER[activeColor.value]

  const data = props.counterclockwise ? [remaining, filled]      : [filled, remaining]
  const bg   = props.counterclockwise ? [GRAY_FILL, fill]        : [fill, GRAY_FILL]
  const bc   = props.counterclockwise ? [GRAY_BORDER, border]    : [border, GRAY_BORDER]

  return { datasets: [{ data, backgroundColor: bg, borderColor: bc, borderWidth: 1, hoverOffset: 2 }] }
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
