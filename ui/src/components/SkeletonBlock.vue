<template>
  <div class="animate-pulse bg-gray-800 rounded" :class="cls" />
</template>

<script setup>
defineProps({ cls: { type: String, default: 'h-4 w-full' } })
</script>
