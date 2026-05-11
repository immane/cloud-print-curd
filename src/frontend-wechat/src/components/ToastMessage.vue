<template>
  <div v-if="show" :class="['toast', type]">{{ text }}</div>
</template>

<script setup lang="ts">
defineProps<{ show: boolean; text: string; type: "info" | "success" | "error" }>();
</script>
