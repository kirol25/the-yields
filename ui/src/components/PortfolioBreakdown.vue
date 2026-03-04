<template>
  <div v-if="items.length > 0" class="flex flex-col items-center gap-6">
    <!-- Donut -->
    <div class="relative shrink-0" style="width:180px;height:180px">
      <Doughnut :data="chartData" :options="chartOptions" />
      <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
        <span class="text-xs text-gray-500 uppercase tracking-wide">Total</span>
        <span class="text-base font-bold text-white">{{ settings.fmt(total) }}</span>
      </div>
    </div>

    <!-- Legend -->
    <div class="w-full space-y-2.5">
      <div v-for="(item, i) in items" :key="item.label" class="flex items-center gap-3 min-w-0">
        <div class="w-2.5 h-2.5 rounded-full shrink-0" :style="{ backgroundColor: COLORS[i % COLORS.length] }" />
        <span class="text-sm text-gray-300 flex-1 truncate">
          {{ item.label }}<span v-if="item.name" class="text-gray-500 ml-1 text-xs">{{ item.name }}</span>
        </span>
        <span class="text-sm tabular-nums" :style="{ color: COLORS[i % COLORS.length] }">{{ settings.fmt(item.amount) }}</span>
        <span class="text-xs text-gray-600 tabular-nums w-9 text-right">{{ item.pct }}%</span>
      </div>
    </div>
  </div>

  <p v-else class="text-sm text-gray-600 text-center py-8">{{ t('dashboard.noDataForYear', { year: store.currentYear }) }}</p>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip } from 'chart.js'
import { useDataStore } from '../stores/dataStore.js'
import { useSettingsStore } from '../stores/settingsStore.js'

ChartJS.register(ArcElement, Tooltip)

const { t } = useI18n()
const store = useDataStore()
const settings = useSettingsStore()

const COLORS = [
  '#10b981', // emerald
  '#60a5fa', // blue
  '#f59e0b', // amber
  '#a78bfa', // violet
  '#fb7185', // rose
  '#34d399', // emerald-light
  '#38bdf8', // sky
  '#c084fc', // purple
  '#f97316', // orange
  '#4ade80', // green
]

const props = defineProps({
  section: { type: String, default: 'dividends' }, // 'dividends' | 'yields'
})

const items = computed(() => {
  const data = store.yearData[props.section] || {}
  const result = []

  for (const [key, entry] of Object.entries(data)) {
    const amount = Object.values(entry.months || {}).reduce((a, b) => a + b, 0)
    if (amount > 0) result.push({ label: key, name: entry.name || '', amount })
  }

  result.sort((a, b) => b.amount - a.amount)

  const total = result.reduce((s, i) => s + i.amount, 0)
  return result.map((item, idx) => ({
    ...item,
    pct: total > 0 ? Math.round((item.amount / total) * 100) : 0,
    color: COLORS[idx % COLORS.length],
  }))
})

const total = computed(() => items.value.reduce((s, i) => s + i.amount, 0))

const chartData = computed(() => ({
  labels: items.value.map((i) => i.label),
  datasets: [{
    data: items.value.map((i) => i.amount),
    backgroundColor: items.value.map((i) => i.color + 'cc'),
    borderColor: items.value.map((i) => i.color),
    borderWidth: 1,
    hoverOffset: 4,
  }],
}))

const chartOptions = {
  cutout: '68%',
  responsive: true,
  maintainAspectRatio: true,
  animation: { duration: 600, easing: 'easeInOutQuart' },
  plugins: {
    legend: { display: false },
    tooltip: { enabled: false },
  },
}
</script>
