<template>
  <div v-if="items.length > 0" class="flex flex-col items-center gap-6">
    <!-- Donut -->
    <div class="relative shrink-0 cursor-pointer" style="width:180px;height:180px">
      <Doughnut :data="chartData" :options="chartOptions" />
      <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
        <template v-if="activeItem">
          <span class="text-xs text-gray-500 uppercase tracking-wide truncate max-w-[120px] text-center">{{ activeItem.name || activeItem.label }}</span>
          <span class="text-base font-bold text-white">{{ settings.fmt(activeItem.amount) }}</span>
          <span class="text-xs text-gray-500">{{ activeItem.pct }}%</span>
        </template>
        <template v-else>
          <span class="text-xs text-gray-500 uppercase tracking-wide">Total</span>
          <span class="text-base font-bold text-white">{{ settings.fmt(total) }}</span>
        </template>
      </div>
    </div>

    <!-- Legend -->
    <div class="w-full space-y-2.5">
      <div
        v-for="(item, i) in items"
        :key="item.label"
        class="flex items-center gap-3 min-w-0 cursor-pointer rounded-lg px-1 py-0.5 transition-opacity"
        :class="selectedLabel && selectedLabel !== item.label ? 'opacity-35' : 'opacity-100'"
        @click="onLegendClick(item.label)"
      >
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
import { computed, ref } from 'vue'
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
  '#10b981',
  '#60a5fa',
  '#f59e0b',
  '#a78bfa',
  '#fb7185',
  '#34d399',
  '#38bdf8',
  '#c084fc',
  '#f97316',
  '#4ade80',
]

const props = defineProps({
  section: { type: String, default: 'dividends' },
})

const selectedLabel = ref(null)

function onLegendClick(label) {
  selectedLabel.value = selectedLabel.value === label ? null : label
}

function handleClick(_, elements) {
  if (!elements.length) return
  const label = items.value[elements[0].index]?.label
  selectedLabel.value = selectedLabel.value === label ? null : label
}

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

const activeItem = computed(() =>
  selectedLabel.value ? items.value.find((i) => i.label === selectedLabel.value) ?? null : null,
)

const total = computed(() => items.value.reduce((s, i) => s + i.amount, 0))

const chartData = computed(() => ({
  labels: items.value.map((i) => i.label),
  datasets: [{
    data: items.value.map((i) => i.amount),
    backgroundColor: items.value.map((i) =>
      !selectedLabel.value || i.label === selectedLabel.value ? i.color + 'cc' : i.color + '22',
    ),
    borderColor: items.value.map((i) =>
      !selectedLabel.value || i.label === selectedLabel.value ? i.color : i.color + '33',
    ),
    borderWidth: 1,
    hoverOffset: 6,
  }],
}))

const chartOptions = computed(() => ({
  cutout: '68%',
  responsive: true,
  maintainAspectRatio: true,
  animation: { duration: 300, easing: 'easeInOutQuart' },
  onClick: handleClick,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx) => {
          const item = items.value[ctx.dataIndex]
          return ` ${item?.name || ctx.label}: ${settings.fmt(ctx.parsed)}`
        },
      },
    },
  },
}))
</script>
