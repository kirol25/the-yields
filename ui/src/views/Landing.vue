<template>
  <div>
    <!-- ── Hero ─────────────────────────────────────────────────────────────── -->
    <section class="min-h-[calc(100vh-65px)] flex items-center">
      <div class="max-w-7xl mx-auto px-6 w-full py-20">
        <div class="grid lg:grid-cols-2 gap-16 items-center">

          <!-- Copy -->
          <div class="space-y-8">
            <span class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              {{ t('landing.badge') }}
            </span>

            <h1 class="text-4xl sm:text-5xl font-bold text-gray-100 leading-tight tracking-tight">
              {{ t('landing.heroTitle') }}
            </h1>

            <p class="text-lg text-gray-400 leading-relaxed max-w-md">
              {{ t('landing.heroSub') }}
            </p>

            <div class="flex items-center gap-3">
              <RouterLink
                to="/login"
                class="inline-flex items-center gap-2 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg transition-colors"
              >
                {{ t('landing.cta') }}
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
                </svg>
              </RouterLink>
            </div>
          </div>

          <!-- Mock app preview -->
          <div class="hidden lg:block">
            <div class="bg-gray-900 border border-gray-800 rounded-2xl p-5 shadow-2xl">
              <!-- Mock header -->
              <div class="flex items-center justify-between mb-5">
                <span class="text-sm font-semibold text-gray-100">Dashboard — 2026</span>
                <div class="flex gap-1.5">
                  <span class="w-2.5 h-2.5 rounded-full bg-gray-700"></span>
                  <span class="w-2.5 h-2.5 rounded-full bg-gray-700"></span>
                  <span class="w-2.5 h-2.5 rounded-full bg-gray-700"></span>
                </div>
              </div>

              <!-- Mock chart -->
              <div class="bg-gray-800/50 rounded-xl p-4 mb-4">
                <p class="text-xs text-gray-500 mb-3">Monthly income</p>
                <div class="flex items-end gap-1.5 h-24">
                  <div v-for="bar in mockBars" :key="bar.month" class="flex-1 flex flex-col items-center gap-1">
                    <div class="w-full flex flex-col-reverse gap-0.5">
                      <div class="w-full bg-emerald-500/70 rounded-sm" :style="{ height: bar.div + 'px' }"></div>
                      <div class="w-full bg-blue-400/60 rounded-sm" :style="{ height: bar.yield + 'px' }"></div>
                    </div>
                    <span class="text-[9px] text-gray-600">{{ bar.month }}</span>
                  </div>
                </div>
              </div>

              <!-- Mock ticker rows -->
              <div class="space-y-2">
                <div v-for="row in mockTickers" :key="row.ticker" class="flex items-center justify-between px-3 py-2 bg-gray-800/40 rounded-lg">
                  <div class="flex items-center gap-2.5">
                    <span class="font-mono text-xs font-semibold text-emerald-400">{{ row.ticker }}</span>
                    <span class="text-xs text-gray-500">{{ row.name }}</span>
                  </div>
                  <span class="text-xs font-medium text-gray-300">{{ row.amount }}</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>

    <!-- ── Features ──────────────────────────────────────────────────────────── -->
    <section class="py-24 bg-gray-900/40 border-y border-gray-800">
      <div class="max-w-7xl mx-auto px-6">
        <div class="grid md:grid-cols-3 gap-8">
          <div v-for="f in features" :key="f.title" class="space-y-4">
            <div class="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400" v-html="f.icon"></div>
            <h3 class="text-base font-semibold text-gray-100">{{ f.title }}</h3>
            <p class="text-sm text-gray-400 leading-relaxed">{{ f.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── How it works ──────────────────────────────────────────────────────── -->
    <section class="py-24">
      <div class="max-w-7xl mx-auto px-6">
        <h2 class="text-2xl font-bold text-gray-100 text-center mb-14">{{ t('landing.howTitle') }}</h2>
        <div class="grid md:grid-cols-3 gap-8 relative">
          <!-- connecting line -->
          <div class="hidden md:block absolute top-5 left-[calc(16.66%+1rem)] right-[calc(16.66%+1rem)] h-px bg-gray-800"></div>

          <div v-for="(step, i) in steps" :key="i" class="text-center space-y-4 relative">
            <div class="w-10 h-10 rounded-full bg-gray-900 border border-gray-700 flex items-center justify-center text-sm font-bold text-emerald-400 mx-auto relative z-10">
              {{ i + 1 }}
            </div>
            <h3 class="text-sm font-semibold text-gray-100">{{ step.title }}</h3>
            <p class="text-sm text-gray-400">{{ step.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── CTA ───────────────────────────────────────────────────────────────── -->
    <section class="py-24 border-t border-gray-800">
      <div class="max-w-xl mx-auto px-6 text-center space-y-6">
        <h2 class="text-3xl font-bold text-gray-100 tracking-tight">{{ t('landing.ctaTitle') }}</h2>
        <p class="text-gray-400">{{ t('landing.ctaSub') }}</p>
        <RouterLink
          to="/login"
          class="inline-flex items-center gap-2 px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg transition-colors"
        >
          {{ t('landing.signIn') }}
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
          </svg>
        </RouterLink>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const mockBars = [
  { month: 'Jan', div: 12, yield: 20 },
  { month: 'Feb', div: 18, yield: 20 },
  { month: 'Mar', div: 10, yield: 22 },
  { month: 'Apr', div: 24, yield: 22 },
  { month: 'May', div: 16, yield: 25 },
  { month: 'Jun', div: 28, yield: 25 },
  { month: 'Jul', div: 14, yield: 28 },
  { month: 'Aug', div: 22, yield: 28 },
  { month: 'Sep', div: 15, yield: 30 },
  { month: 'Oct', div: 30, yield: 30 },
  { month: 'Nov', div: 19, yield: 32 },
  { month: 'Dec', div: 35, yield: 32 },
]

const mockTickers = [
  { ticker: 'AAPL', name: 'Apple Inc.', amount: '€ 42.50' },
  { ticker: 'MSFT', name: 'Microsoft', amount: '€ 28.00' },
  { ticker: 'SCHD', name: 'Schwab Dividend', amount: '€ 61.20' },
]

const features = computed(() => [
  {
    title: t('landing.feature1Title'),
    desc: t('landing.feature1Desc'),
    icon: '<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>',
  },
  {
    title: t('landing.feature2Title'),
    desc: t('landing.feature2Desc'),
    icon: '<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
  },
  {
    title: t('landing.feature3Title'),
    desc: t('landing.feature3Desc'),
    icon: '<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>',
  },
])

const steps = computed(() => [
  { title: t('landing.step1Title'), desc: t('landing.step1Desc') },
  { title: t('landing.step2Title'), desc: t('landing.step2Desc') },
  { title: t('landing.step3Title'), desc: t('landing.step3Desc') },
])
</script>
