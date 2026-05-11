<template>
  <div v-if="open && resource" class="modal" @click="$emit('close')">
    <div class="modal-card" @click.stop>
      <h3>{{ resource.title }}</h3>
      <img :src="resource.preview_url || resource.thumbnail_url || fallback" class="full-img" />
      <button class="primary" @click="$emit('order', resource)">Order</button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ open: boolean; resource: any | null; fallback: string }>();
defineEmits(["close", "order"]);
</script>
