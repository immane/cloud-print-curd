<template>
  <div v-if="open" class="modal" @click="$emit('close')">
    <div class="modal-card full" @click.stop>
      <img :src="imageUrl" alt="tutorial" class="full-img" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ open: boolean; imageUrl: string }>();
defineEmits(["close"]);
</script>
