<template>
  <div v-if="open" class="modal" @click="$emit('close')">
    <div class="modal-card" @click.stop>
      <h3>FAQ</h3>
      <ul>
        <li>How long does printing take? Usually same day for small jobs.</li>
        <li>Can I request refund? Yes, contact support before printing starts.</li>
        <li>How is price calculated? By pages, size, color and duplex options.</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ open: boolean }>();
defineEmits(["close"]);
</script>
