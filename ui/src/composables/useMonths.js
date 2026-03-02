import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const MONTH_VALUES = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

export function useMonths() {
  const { t } = useI18n()

  const months = computed(() =>
    MONTH_VALUES.map((value) => ({
      value,
      short: t(`months.${value}.short`),
      label: t(`months.${value}.label`),
    })),
  )

  return { months }
}
