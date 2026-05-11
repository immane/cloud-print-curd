<template>
  <nav class="tabbar">
    <button :class="{ active: tab === 'home' }" @click="$emit('change', 'home')">Home</button>
    <button :class="{ active: tab === 'library' }" @click="$emit('change', 'library')">Library</button>
    <button :class="{ active: tab === 'me' }" @click="$emit('change', 'me')">Me</button>
  </nav>
</template>

<script setup lang="ts">
defineProps<{ tab: "home" | "library" | "me" }>();
defineEmits(["change"]);
</script>
