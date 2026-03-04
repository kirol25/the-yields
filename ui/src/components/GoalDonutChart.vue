<template>
  <div class="relative" :style="{ width: `${size}px`, height: `${size}px` }">
    <Doughnut :data="chartData" :options="chartOptions" />
    <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
      <span class="text-xl font-bold text-white tabular-nums">{{ pct }}%</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip } from 'chart.js'

ChartJS.register(ArcElement, Tooltip)

const props = defineProps({
  achieved: { type: Number, required: true },
  goal:     { type: Number, required: true },
  size:     { type: Number, default: 140 },
})

const pct = computed(() =>
  props.goal > 0 ? Math.min(Math.round((props.achieved / props.goal) * 100), 100) : 0,
)

const chartData = computed(() => ({
  datasets: [{
    data: [
      Math.min(props.achieved, props.goal),
      Math.max(props.goal - props.achieved, 0),
    ],
    backgroundColor: ['rgba(52, 211, 153, 0.9)', 'rgba(31, 41, 55, 0.8)'],
    borderColor:     ['rgb(52, 211, 153)', 'rgb(55, 65, 81)'],
    borderWidth: 1,
    hoverOffset: 2,
  }],
}))

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
